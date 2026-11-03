from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models.auth import User
from app.models.company import Company, CompanyDocument, CompanyMember
from app.schemas.company import CompanyResponse, CompanyUpdate
from app.services.cv_files import clean_original_name, private_company_docs_dir


router = APIRouter(prefix="/companies/me", tags=["company profile"])
MAX_DOCUMENT_BYTES = 10 * 1024 * 1024


class CompanyDocumentResponse(BaseModel):
    id: str
    original_name: str
    document_type: str
    media_type: str
    size_bytes: int
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


def get_my_company(db: Session, user: User) -> Company:
    membership = db.scalar(select(CompanyMember).where(CompanyMember.user_id == user.id))
    if not membership:
        raise HTTPException(status_code=404, detail="Tài khoản chưa liên kết với công ty")
    company = db.get(Company, membership.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ công ty")
    return company


def require_company_editor(db: Session, user: User) -> None:
    membership = db.scalar(select(CompanyMember).where(CompanyMember.user_id == user.id))
    if not membership or membership.role not in {"owner", "manager"}:
        raise HTTPException(status_code=403, detail="Vai trò thành viên công ty không có quyền chỉnh sửa hồ sơ hoặc giấy tờ")


@router.get("", response_model=CompanyResponse)
def read_company(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Chức năng này chỉ dành cho nhà tuyển dụng")
    return get_my_company(db, user)


@router.patch("", response_model=CompanyResponse)
def update_company(
    payload: CompanyUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Chức năng này chỉ dành cho nhà tuyển dụng")
    require_company_editor(db, user)
    company = get_my_company(db, user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        if key == "website" and value is not None:
            value = str(value)
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return company


@router.get("/documents", response_model=list[CompanyDocumentResponse])
def list_documents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Chức năng này chỉ dành cho nhà tuyển dụng")
    company = get_my_company(db, user)
    return list(db.scalars(select(CompanyDocument).where(CompanyDocument.company_id == company.id).order_by(CompanyDocument.created_at.desc())))


@router.post("/documents", response_model=CompanyDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Chức năng này chỉ dành cho nhà tuyển dụng")
    require_company_editor(db, user)
    company = get_my_company(db, user)
    name = clean_original_name(file.filename)
    suffix = Path(name).suffix.lower()
    if suffix not in {".pdf", ".png", ".jpg", ".jpeg"}:
        raise HTTPException(status_code=415, detail="Chỉ chấp nhận giấy tờ PDF, PNG hoặc JPG")
    content = await file.read(MAX_DOCUMENT_BYTES + 1)
    await file.close()
    if not content:
        raise HTTPException(status_code=400, detail="Tệp tải lên đang trống")
    if len(content) > MAX_DOCUMENT_BYTES:
        raise HTTPException(status_code=413, detail="Tệp không được vượt quá 10 MB")
    if suffix == ".pdf":
        media_type = "application/pdf"
        valid = content.startswith(b"%PDF-")
    elif suffix == ".png":
        media_type = "image/png"
        valid = content.startswith(b"\x89PNG\r\n\x1a\n")
    else:
        media_type = "image/jpeg"
        valid = content.startswith(b"\xff\xd8\xff")
    if not valid:
        raise HTTPException(status_code=415, detail="Nội dung tệp không khớp với định dạng đã chọn")

    storage_name = f"{uuid4().hex}{suffix}"
    path = private_company_docs_dir() / storage_name
    path.write_bytes(content)
    try:
        document = CompanyDocument(
            company_id=company.id,
            uploaded_by=user.id,
            storage_name=storage_name,
            original_name=name,
            document_type="business_registration",
            media_type=media_type,
            size_bytes=len(content),
            status="pending",
        )
        company.verification_status = "pending"
        company.verification_note = None
        company.verified_at = None
        db.add(document)
        db.commit()
        db.refresh(document)
        return document
    except Exception:
        db.rollback()
        path.unlink(missing_ok=True)
        raise


@router.get("/documents/{document_id}/download")
def download_own_document(
    document_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Chức năng này chỉ dành cho nhà tuyển dụng")
    company = get_my_company(db, user)
    document = db.scalar(select(CompanyDocument).where(
        CompanyDocument.id == document_id,
        CompanyDocument.company_id == company.id,
    ))
    if not document:
        raise HTTPException(status_code=404, detail="Không tìm thấy giấy tờ")
    path = (private_company_docs_dir() / document.storage_name).resolve()
    if path.parent != private_company_docs_dir() or not path.is_file():
        raise HTTPException(status_code=404, detail="Không tìm thấy tệp giấy tờ")
    return FileResponse(path, media_type=document.media_type, filename=document.original_name)
