import re
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from docx import Document
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.api.v1.students import require_student
from app.db.session import get_db
from app.models.auth import User
from app.models.student import StudentCV
from app.services.cv_files import delete_cv_file, read_and_validate_cv, store_cv


router = APIRouter(prefix="/students/me/cvs", tags=["student CVs"])
MAX_EXTRACTED_TEXT = 1_000_000
SKILL_TERMS = {
    "react": "React", "typescript": "TypeScript", "javascript": "JavaScript",
    "python": "Python", "java": "Java", "node.js": "Node.js", "sql": "SQL",
    "figma": "Figma", "git": "Git", "docker": "Docker", "html": "HTML",
    "css": "CSS", "fastapi": "FastAPI", "postgresql": "PostgreSQL",
}


class CVResponse(BaseModel):
    id: str
    original_name: str
    media_type: str
    size_bytes: int
    is_default: bool
    parse_status: str
    parsed_json: dict | None
    parse_error: str | None
    created_at: datetime

    class Config:
        from_attributes = True


def owned_cv(db: Session, student_id: str, cv_id: str) -> StudentCV:
    cv = db.scalar(select(StudentCV).where(StudentCV.id == cv_id, StudentCV.student_id == student_id))
    if cv is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy CV")
    return cv


@router.get("", response_model=list[CVResponse])
def list_cvs(user: User = Depends(require_student), db: Session = Depends(get_db)):
    return list(db.scalars(select(StudentCV).where(StudentCV.student_id == user.id).order_by(StudentCV.created_at.desc())))


@router.post("", response_model=CVResponse, status_code=status.HTTP_201_CREATED)
async def upload_cv(
    file: UploadFile = File(...),
    user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    content, original_name, media_type = await read_and_validate_cv(file)
    suffix = Path(original_name).suffix.lower()
    storage_name = store_cv(content, suffix)
    try:
        existing = list(db.scalars(select(StudentCV).where(StudentCV.student_id == user.id)))
        make_default = not existing
        if make_default:
            for cv in existing:
                cv.is_default = False
        cv = StudentCV(
            student_id=user.id,
            original_name=original_name,
            storage_name=storage_name,
            media_type=media_type,
            size_bytes=len(content),
            is_default=make_default,
        )
        db.add(cv)
        db.commit()
        db.refresh(cv)
        return cv
    except Exception:
        db.rollback()
        delete_cv_file(storage_name)
        raise
    finally:
        await file.close()


@router.put("/{cv_id}/default", response_model=CVResponse)
def set_default_cv(cv_id: str, user: User = Depends(require_student), db: Session = Depends(get_db)):
    selected = owned_cv(db, user.id, cv_id)
    for cv in db.scalars(select(StudentCV).where(StudentCV.student_id == user.id)):
        cv.is_default = cv.id == selected.id
    db.commit()
    db.refresh(selected)
    return selected


@router.delete("/{cv_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cv(cv_id: str, user: User = Depends(require_student), db: Session = Depends(get_db)):
    cv = owned_cv(db, user.id, cv_id)
    was_default = cv.is_default
    storage_name = cv.storage_name
    db.delete(cv)
    db.flush()
    if was_default:
        replacement = db.scalar(select(StudentCV).where(StudentCV.student_id == user.id).order_by(StudentCV.created_at.desc()))
        if replacement:
            replacement.is_default = True
    db.commit()
    delete_cv_file(storage_name)


@router.post("/{cv_id}/parse", response_model=CVResponse)
def parse_cv(cv_id: str, user: User = Depends(require_student), db: Session = Depends(get_db)):
    cv = owned_cv(db, user.id, cv_id)
    from app.core.config import get_settings

    storage_dir = get_settings().upload_dir
    if not storage_dir.is_absolute():
        storage_dir = Path(__file__).resolve().parents[2] / storage_dir
    path = (storage_dir / cv.storage_name).resolve()
    if path.parent != storage_dir.resolve() or not path.is_file():
        raise HTTPException(status_code=404, detail="Không tìm thấy tệp CV")

    try:
        content = path.read_bytes()
        if cv.media_type == "application/pdf":
            reader = PdfReader(BytesIO(content), strict=False)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            document = Document(BytesIO(content))
            text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        text = text.replace("\x00", "")[:MAX_EXTRACTED_TEXT]
        if not text.strip():
            raise ValueError("Không trích xuất được văn bản; có thể đây là CV scan hoặc tệp rỗng.")
        email_match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.IGNORECASE)
        phone_match = re.search(r"(?<!\w)(?:\+?84|0)(?:[ .-]?\d){8,10}(?!\w)", text)
        lower_text = text.casefold()
        found_skills = [label for key, label in SKILL_TERMS.items() if re.search(rf"(?<![\w]){re.escape(key)}(?![\w])", lower_text)]
        parsed = {
            "email": email_match.group(0) if email_match else None,
            "phone": phone_match.group(0) if phone_match else None,
            "skills": found_skills,
            "confidence": {
                "email": 0.98 if email_match else 0.0,
                "phone": 0.75 if phone_match else 0.0,
                "skills": 0.55 if found_skills else 0.0,
            },
            "review_required": True,
            "parser": "local-regex-v1",
        }
        cv.extracted_text = text
        cv.parsed_json = parsed
        cv.parse_status = "complete"
        cv.parse_error = None
    except Exception as exc:
        cv.parse_status = "failed"
        cv.parse_error = str(exc)[:300]
        cv.parsed_json = None
    db.commit()
    db.refresh(cv)
    return cv
