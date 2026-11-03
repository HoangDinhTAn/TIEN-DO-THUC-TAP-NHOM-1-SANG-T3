from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.api.v1.students import require_student
from app.db.session import get_db
from app.models.auth import User
from app.models.company import Company, CompanyMember
from app.models.jobs import Job, JobApplication
from app.models.student import StudentCV
from app.schemas.jobs import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationStatusUpdate,
    JobCreate,
    JobResponse,
    RecruiterApplicationResponse,
)
from app.services.cv_files import cv_storage_dir


router = APIRouter(tags=["jobs and applications"])


def require_recruiter(user: User = Depends(get_current_user)) -> User:
    if user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Chỉ tài khoản nhà tuyển dụng mới được quản lý tin tuyển dụng")
    return user


def company_for_recruiter(db: Session, user: User, *, write: bool = False) -> Company:
    membership = db.scalar(select(CompanyMember).where(CompanyMember.user_id == user.id))
    company = db.get(Company, membership.company_id) if membership else None
    if not company:
        raise HTTPException(status_code=403, detail="Tài khoản nhà tuyển dụng chưa liên kết doanh nghiệp")
    if write and membership.role not in {"owner", "manager", "recruiter"}:
        raise HTTPException(status_code=403, detail="Vai trò thành viên công ty không được quản lý tin hoặc hồ sơ ứng viên")
    return company


def job_response(db: Session, job: Job) -> dict:
    company = db.get(Company, job.company_id)
    return {**{key: getattr(job, key) for key in (
        "id", "company_id", "title", "description", "location", "employment_type",
        "salary_min", "salary_max", "skills", "status", "created_at",
    )}, "company_name": company.name if company else "Doanh nghiệp", "company_verified": bool(company and company.verification_status == "verified")}


def application_response(db: Session, application: JobApplication) -> dict:
    job = db.get(Job, application.job_id)
    company = db.get(Company, job.company_id) if job else None
    return {
        "id": application.id,
        "job_id": application.job_id,
        "student_id": application.student_id,
        "job_title": job.title if job else "Tin tuyển dụng đã đóng",
        "company_name": company.name if company else "Doanh nghiệp",
        "cv_id": application.cv_id,
        "status": application.status,
        "created_at": application.created_at,
    }


@router.get("/jobs", response_model=list[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.scalars(select(Job).join(Company, Company.id == Job.company_id).where(Job.status == "published", Company.verification_status == "verified").order_by(Job.created_at.desc()))
    return [job_response(db, job) for job in jobs]


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, user: User = Depends(require_recruiter), db: Session = Depends(get_db)):
    company = company_for_recruiter(db, user, write=True)
    if payload.salary_min is not None and payload.salary_max is not None and payload.salary_min > payload.salary_max:
        raise HTTPException(status_code=422, detail="Mức lương tối thiểu không được lớn hơn mức tối đa")
    job_status = "published" if company.verification_status == "verified" else "draft"
    job = Job(company_id=company.id, created_by=user.id, **payload.model_dump(), status=job_status)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job_response(db, job)


@router.patch("/jobs/{job_id}", response_model=JobResponse)
def update_job(job_id: str, payload: JobCreate, user: User = Depends(require_recruiter), db: Session = Depends(get_db)):
    company = company_for_recruiter(db, user, write=True)
    job = db.scalar(select(Job).where(Job.id == job_id, Job.company_id == company.id))
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin thuộc doanh nghiệp của bạn")
    if payload.salary_min is not None and payload.salary_max is not None and payload.salary_min > payload.salary_max:
        raise HTTPException(status_code=422, detail="Mức lương tối thiểu không được lớn hơn mức tối đa")
    for key, value in payload.model_dump().items():
        setattr(job, key, value)
    db.commit()
    db.refresh(job)
    return job_response(db, job)


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def close_job(job_id: str, user: User = Depends(require_recruiter), db: Session = Depends(get_db)):
    company = company_for_recruiter(db, user, write=True)
    job = db.scalar(select(Job).where(Job.id == job_id, Job.company_id == company.id))
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin thuộc doanh nghiệp của bạn")
    job.status = "closed"
    db.commit()


@router.get("/recruiter/jobs", response_model=list[JobResponse])
def list_my_jobs(user: User = Depends(require_recruiter), db: Session = Depends(get_db)):
    company = company_for_recruiter(db, user)
    jobs = db.scalars(select(Job).where(Job.company_id == company.id).order_by(Job.created_at.desc()))
    return [job_response(db, job) for job in jobs]


@router.post("/jobs/{job_id}/publish", response_model=JobResponse)
def publish_job(job_id: str, user: User = Depends(require_recruiter), db: Session = Depends(get_db)):
    company = company_for_recruiter(db, user, write=True)
    job = db.scalar(select(Job).where(Job.id == job_id, Job.company_id == company.id))
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin thuộc doanh nghiệp của bạn")
    job.status = "published"
    db.commit()
    db.refresh(job)
    return job_response(db, job)


@router.post("/jobs/{job_id}/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_to_job(
    job_id: str,
    payload: ApplicationCreate,
    user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    job = db.scalar(select(Job).join(Company, Company.id == Job.company_id).where(Job.id == job_id, Job.status == "published", Company.verification_status == "verified"))
    if not job:
        raise HTTPException(status_code=404, detail="Tin tuyển dụng không tồn tại hoặc đã đóng")
    if db.scalar(select(JobApplication.id).where(JobApplication.job_id == job_id, JobApplication.student_id == user.id)):
        raise HTTPException(status_code=409, detail="Bạn đã ứng tuyển vị trí này rồi")
    cv_id = payload.cv_id or db.scalar(select(StudentCV.id).where(
        StudentCV.student_id == user.id,
        StudentCV.is_default.is_(True),
    ))
    if cv_id and not db.scalar(select(StudentCV.id).where(StudentCV.id == cv_id, StudentCV.student_id == user.id)):
        raise HTTPException(status_code=404, detail="Không tìm thấy CV của bạn")
    application = JobApplication(
        job_id=job.id,
        student_id=user.id,
        cv_id=cv_id,
        cover_letter=payload.cover_letter,
    )
    db.add(application)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Bạn đã ứng tuyển vị trí này rồi") from exc
    db.refresh(application)
    return application_response(db, application)


@router.get("/applications/me", response_model=list[ApplicationResponse])
def list_my_applications(user: User = Depends(require_student), db: Session = Depends(get_db)):
    applications = db.scalars(select(JobApplication).where(JobApplication.student_id == user.id).order_by(JobApplication.created_at.desc()))
    return [application_response(db, application) for application in applications]


@router.delete("/applications/me/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def withdraw_application(application_id: str, user: User = Depends(require_student), db: Session = Depends(get_db)):
    application = db.scalar(select(JobApplication).where(
        JobApplication.id == application_id,
        JobApplication.student_id == user.id,
    ))
    if not application:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn ứng tuyển của bạn")
    if application.status in {"rejected", "withdrawn"}:
        raise HTTPException(status_code=409, detail="Đơn này đã kết thúc và không thể rút")
    application.status = "withdrawn"
    db.commit()


@router.get("/recruiter/jobs/{job_id}/applications", response_model=list[RecruiterApplicationResponse])
def list_job_applications(job_id: str, user: User = Depends(require_recruiter), db: Session = Depends(get_db)):
    company = company_for_recruiter(db, user, write=True)
    job = db.scalar(select(Job).where(Job.id == job_id, Job.company_id == company.id))
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin thuộc doanh nghiệp của bạn")
    applications = db.scalars(select(JobApplication).where(JobApplication.job_id == job.id).order_by(JobApplication.created_at.desc()))
    return [{
        "id": application.id,
        "job_id": job.id,
        "job_title": job.title,
        "student_id": application.student_id,
        "student_name": db.get(User, application.student_id).full_name,
        "cv_id": application.cv_id,
        "status": application.status,
        "created_at": application.created_at,
    } for application in applications if db.get(User, application.student_id)]


def owned_company_application(db: Session, user: User, application_id: str) -> JobApplication:
    company = company_for_recruiter(db, user, write=True)
    application = db.scalar(
        select(JobApplication)
        .join(Job, Job.id == JobApplication.job_id)
        .where(JobApplication.id == application_id, Job.company_id == company.id)
    )
    if not application:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn ứng tuyển thuộc doanh nghiệp của bạn")
    return application


@router.patch("/recruiter/applications/{application_id}")
def update_application_status(
    application_id: str,
    payload: ApplicationStatusUpdate,
    user: User = Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    application = owned_company_application(db, user, application_id)
    if application.status in {"rejected", "withdrawn"}:
        raise HTTPException(status_code=409, detail="Đơn ứng tuyển đã kết thúc")
    allowed_transitions = {
        "submitted": {"viewed", "interview", "rejected"},
        "viewed": {"interview", "rejected"},
        "interview": {"rejected"},
    }
    if payload.status not in allowed_transitions.get(application.status, set()):
        raise HTTPException(status_code=409, detail="Trạng thái đơn ứng tuyển không thể chuyển theo hướng này")
    application.status = payload.status
    db.commit()
    return {"id": application.id, "status": application.status}


@router.get("/recruiter/applications/{application_id}/cv")
def download_applicant_cv(application_id: str, user: User = Depends(require_recruiter), db: Session = Depends(get_db)):
    application = owned_company_application(db, user, application_id)
    if not application.cv_id:
        raise HTTPException(status_code=404, detail="Ứng viên chưa đính kèm CV")
    cv = db.get(StudentCV, application.cv_id)
    if not cv or cv.student_id != application.student_id:
        raise HTTPException(status_code=404, detail="Không tìm thấy CV đã nộp")
    directory = cv_storage_dir()
    path = (directory / cv.storage_name).resolve()
    if path.parent != directory or not path.is_file():
        raise HTTPException(status_code=404, detail="Không tìm thấy tệp CV")
    return FileResponse(path, media_type=cv.media_type, filename=cv.original_name)

