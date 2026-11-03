from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.auth import User, utc_now
from app.models.audit import AuditLog
from app.models.company import Company, CompanyDocument, CompanyMember
from app.models.jobs import Job
from app.schemas.company import CompanyRejectRequest, CompanyReviewRequest
from app.services.cv_files import private_company_docs_dir


router = APIRouter(prefix="/admin", tags=["administration"])


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role not in {"platform_admin", "moderator"}:
        raise HTTPException(status_code=403, detail="Chỉ quản trị viên được phép thực hiện thao tác này")
    return user


@router.get("/companies/pending")
def pending_companies(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    companies = list(db.scalars(select(Company).where(Company.verification_status == "pending").order_by(Company.created_at.asc())))
    result = []
    for company in companies:
        members = list(db.scalars(select(CompanyMember).where(CompanyMember.company_id == company.id)))
        documents = list(db.scalars(select(CompanyDocument).where(CompanyDocument.company_id == company.id).order_by(CompanyDocument.created_at.desc())))
        result.append({
            "id": company.id,
            "name": company.name,
            "tax_code": company.tax_code,
            "industry": company.industry,
            "website": company.website,
            "description": company.description,
            "verification_status": company.verification_status,
            "verification_note": company.verification_note,
            "created_at": company.created_at,
            "members": [{"name": db.get(User, member.user_id).full_name, "email": db.get(User, member.user_id).email, "title": member.title} for member in members if db.get(User, member.user_id)],
            "documents": [{
                "id": doc.id,
                "original_name": doc.original_name,
                "document_type": doc.document_type,
                "media_type": doc.media_type,
                "size_bytes": doc.size_bytes,
                "status": doc.status,
            } for doc in documents],
        })
    return result


def get_pending_company(db: Session, company_id: str) -> Company:
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Không tìm thấy công ty")
    if company.verification_status != "pending":
        raise HTTPException(status_code=409, detail="Công ty không còn ở hàng chờ xác minh")
    return company


@router.post("/companies/{company_id}/approve")
def approve_company(
    company_id: str,
    payload: CompanyReviewRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    company = get_pending_company(db, company_id)
    documents = list(db.scalars(select(CompanyDocument).where(
        CompanyDocument.company_id == company.id,
        CompanyDocument.status == "pending",
    )))
    if not documents:
        raise HTTPException(status_code=409, detail="Cần có giấy tờ doanh nghiệp đang chờ duyệt trước khi xác minh")
    now = utc_now()
    company.verification_status = "verified"
    company.verified_at = now
    company.reviewed_at = now
    company.reviewed_by = admin.id
    company.verification_note = payload.note
    for document in documents:
        document.status = "approved"
    db.add(AuditLog(
        actor_id=admin.id,
        action="company.approve",
        entity="company",
        entity_id=company.id,
        details={"note": payload.note, "documents": [doc.id for doc in documents]},
    ))
    db.commit()
    return {"id": company.id, "verification_status": company.verification_status, "verified_at": company.verified_at}


@router.post("/companies/{company_id}/reject")
def reject_company(
    company_id: str,
    payload: CompanyRejectRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    company = get_pending_company(db, company_id)
    now = utc_now()
    company.verification_status = "rejected"
    company.verified_at = None
    company.reviewed_at = now
    company.reviewed_by = admin.id
    company.verification_note = payload.note
    for job in db.scalars(select(Job).where(Job.company_id == company.id)):
        if job.status == "published":
            job.status = "draft"
    for document in db.scalars(select(CompanyDocument).where(
        CompanyDocument.company_id == company.id,
        CompanyDocument.status == "pending",
    )):
        document.status = "rejected"
    db.add(AuditLog(
        actor_id=admin.id,
        action="company.reject",
        entity="company",
        entity_id=company.id,
        details={"note": payload.note},
    ))
    db.commit()
    return {"id": company.id, "verification_status": company.verification_status, "verification_note": company.verification_note}


@router.get("/companies/{company_id}/documents/{document_id}")
def download_company_document(
    company_id: str,
    document_id: str,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    document = db.scalar(select(CompanyDocument).where(
        CompanyDocument.id == document_id,
        CompanyDocument.company_id == company_id,
    ))
    if not document:
        raise HTTPException(status_code=404, detail="Không tìm thấy giấy tờ")
    directory = private_company_docs_dir()
    path = (directory / document.storage_name).resolve()
    if path.parent != directory or not path.is_file():
        raise HTTPException(status_code=404, detail="Không tìm thấy tệp giấy tờ")
    return FileResponse(path, media_type=document.media_type, filename=document.original_name)
