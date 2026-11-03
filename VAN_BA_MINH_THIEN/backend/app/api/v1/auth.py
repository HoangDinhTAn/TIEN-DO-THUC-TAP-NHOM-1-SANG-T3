from datetime import datetime, timedelta, timezone
import smtplib
import logging
from uuid import uuid4

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    hash_password,
    hash_token,
    new_opaque_token,
    verify_password,
)
from app.db.session import get_db
from app.models.auth import AuthSession, Consent, EmailVerification, PasswordReset, User, utc_now
from app.models.company import Company, CompanyMember
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    ResetPasswordRequest,
    RefreshRequest,
    RegisterRequest,
    ResendVerificationRequest,
    TokenResponse,
    UserResponse,
    VerifyEmailRequest,
)
from app.services.email import send_account_email


router = APIRouter(prefix="/auth", tags=["authentication"])
bearer = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


def issue_session(db: Session, user: User) -> TokenResponse:
    settings = get_settings()
    session_id = str(uuid4())
    refresh_token = new_opaque_token()
    expires_at = utc_now() + timedelta(days=settings.refresh_token_days)
    db.add(AuthSession(
        id=session_id,
        user_id=user.id,
        refresh_token_hash=hash_token(refresh_token),
        expires_at=expires_at,
    ))
    access_token = create_access_token(user.id, user.role, session_id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_minutes * 60,
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if not payload.accept_terms or not payload.accept_data_processing:
        raise HTTPException(status_code=422, detail="Cần đồng ý điều khoản và mục đích xử lý dữ liệu")

    email = str(payload.email).strip().lower()
    if payload.role == "recruiter" and db.scalar(select(Company.id).where(Company.tax_code == payload.tax_code)):
        raise HTTPException(status_code=409, detail="Mã số thuế đã được đăng ký")
    user = User(
        email=email,
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    try:
        db.flush()
        if payload.role == "recruiter":
            company = Company(name=payload.company_name.strip(), tax_code=payload.tax_code.strip())
            db.add(company)
            db.flush()
            db.add(CompanyMember(company_id=company.id, user_id=user.id, role="owner", title=payload.job_title.strip()))
        db.add_all([
            Consent(user_id=user.id, purpose="terms_of_service", granted=True, policy_version="1.0"),
            Consent(user_id=user.id, purpose="personal_data_processing", granted=True, policy_version="1.0"),
        ])
        raw_token = new_opaque_token()
        settings = get_settings()
        db.add(EmailVerification(
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=utc_now() + timedelta(minutes=settings.verification_token_minutes),
        ))
        send_account_email(
            email,
            "Xác minh tài khoản Hướng",
            f"Xin chào {user.full_name},\n\nMã xác minh tài khoản của bạn là:\n{raw_token}\n\nMã có hiệu lực trong {settings.verification_token_minutes} phút.",
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email đã được đăng ký") from exc
    except (OSError, smtplib.SMTPException) as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="Chưa gửi được email xác minh; vui lòng thử lại") from exc
    return {"message": "Đã tạo tài khoản. Hãy kiểm tra email để xác minh.", "status": user.status}


@router.post("/verify-email")
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    verification = db.scalar(select(EmailVerification).where(
        EmailVerification.token_hash == hash_token(payload.token),
        EmailVerification.consumed_at.is_(None),
    ))
    if not verification or verification.expires_at <= utc_now():
        raise HTTPException(status_code=400, detail="Mã xác minh không hợp lệ hoặc đã hết hạn")
    user = db.get(User, verification.user_id)
    if not user or user.status != "pending_verification":
        raise HTTPException(status_code=400, detail="Tài khoản không ở trạng thái chờ xác minh")
    verification.consumed_at = utc_now()
    user.email_verified_at = utc_now()
    user.status = "active"
    db.commit()
    return {"message": "Email đã được xác minh. Bạn có thể đăng nhập."}


@router.post("/resend-verification")
def resend_verification(payload: ResendVerificationRequest, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()
    user = db.scalar(select(User).where(User.email == email, User.status == "pending_verification"))
    if user:
        cooldown_since = utc_now() - timedelta(minutes=1)
        recent = db.scalar(select(func.count()).select_from(EmailVerification).where(
            EmailVerification.user_id == user.id,
            EmailVerification.created_at >= cooldown_since,
        ))
        if not recent:
            raw_token = new_opaque_token()
            settings = get_settings()
            db.add(EmailVerification(
                user_id=user.id,
                token_hash=hash_token(raw_token),
                expires_at=utc_now() + timedelta(minutes=settings.verification_token_minutes),
            ))
            try:
                send_account_email(
                    email,
                    "Xác minh tài khoản Hướng",
                    f"Mã xác minh của bạn có hiệu lực trong {settings.verification_token_minutes} phút:\n{raw_token}",
                )
                db.commit()
            except (OSError, smtplib.SMTPException) as exc:
                db.rollback()
                logger.warning("Unable to send verification email")
    return {"message": "Nếu tài khoản đang chờ xác minh, email hướng dẫn sẽ được gửi."}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(payload.email).strip().lower()))
    now = utc_now()
    if not user or user.deleted_at is not None or not verify_password(payload.password, user.password_hash):
        if user and user.deleted_at is None:
            user.failed_login_count += 1
            if user.failed_login_count >= 5:
                user.locked_until = now + timedelta(minutes=15)
                user.failed_login_count = 0
            db.commit()
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")
    if user.locked_until and user.locked_until > now:
        raise HTTPException(status_code=423, detail="Tài khoản tạm khóa. Vui lòng thử lại sau.")
    if user.status != "active" or user.email_verified_at is None:
        raise HTTPException(status_code=403, detail="Vui lòng xác minh email trước khi đăng nhập")
    user.failed_login_count = 0
    user.locked_until = None
    tokens = issue_session(db, user)
    db.commit()
    return tokens


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    old_hash = hash_token(payload.refresh_token)
    session = db.scalar(select(AuthSession).where(AuthSession.refresh_token_hash == old_hash))
    now = utc_now()
    if not session or session.revoked_at is not None or session.expires_at <= now:
        raise HTTPException(status_code=401, detail="Refresh token không hợp lệ hoặc đã hết hạn")
    user = db.get(User, session.user_id)
    if not user or user.status != "active" or user.deleted_at is not None:
        session.revoked_at = now
        db.commit()
        raise HTTPException(status_code=401, detail="Tài khoản không còn hoạt động")
    session.revoked_at = now
    result = issue_session(db, user)
    db.commit()
    return result


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    session = db.scalar(select(AuthSession).where(
        AuthSession.refresh_token_hash == hash_token(payload.refresh_token),
        AuthSession.revoked_at.is_(None),
    ))
    if session:
        session.revoked_at = utc_now()
        db.commit()


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()
    user = db.scalar(select(User).where(User.email == email, User.status == "active", User.deleted_at.is_(None)))
    if user:
        raw_token = new_opaque_token()
        db.add(PasswordReset(
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=utc_now() + timedelta(minutes=30),
        ))
        try:
            send_account_email(
                email,
                "Đặt lại mật khẩu Hướng",
                f"Dùng token sau trong vòng 30 phút để đặt lại mật khẩu:\n{raw_token}\n\nNếu bạn không yêu cầu, hãy bỏ qua email này.",
            )
            db.commit()
        except (OSError, smtplib.SMTPException) as exc:
            db.rollback()
            logger.warning("Unable to send password reset email")
    return {"message": "Nếu email thuộc tài khoản hợp lệ, hướng dẫn đặt lại sẽ được gửi."}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset = db.scalar(select(PasswordReset).where(
        PasswordReset.token_hash == hash_token(payload.token),
        PasswordReset.consumed_at.is_(None),
    ))
    if not reset or reset.expires_at <= utc_now():
        raise HTTPException(status_code=400, detail="Token đặt lại không hợp lệ hoặc đã hết hạn")
    user = db.get(User, reset.user_id)
    if not user or user.status != "active":
        raise HTTPException(status_code=400, detail="Tài khoản không thể đặt lại mật khẩu")
    reset.consumed_at = utc_now()
    user.password_hash = hash_password(payload.new_password)
    user.failed_login_count = 0
    user.locked_until = None
    sessions = db.scalars(select(AuthSession).where(
        AuthSession.user_id == user.id,
        AuthSession.revoked_at.is_(None),
    ))
    for session in sessions:
        session.revoked_at = utc_now()
    db.commit()
    return {"message": "Mật khẩu đã được đặt lại. Hãy đăng nhập lại."}


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Cần đăng nhập")
    try:
        claims = jwt.decode(credentials.credentials, get_settings().jwt_secret, algorithms=["HS256"])
        if claims.get("type") != "access":
            raise jwt.InvalidTokenError("wrong token type")
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Access token không hợp lệ hoặc đã hết hạn") from exc
    session = db.get(AuthSession, claims.get("sid"))
    if not session or session.revoked_at is not None or session.expires_at <= utc_now():
        raise HTTPException(status_code=401, detail="Phiên đăng nhập đã hết hạn")
    user = db.get(User, claims.get("sub"))
    if not user or user.status != "active" or user.deleted_at is not None:
        raise HTTPException(status_code=401, detail="Tài khoản không còn hoạt động")
    return user


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user
