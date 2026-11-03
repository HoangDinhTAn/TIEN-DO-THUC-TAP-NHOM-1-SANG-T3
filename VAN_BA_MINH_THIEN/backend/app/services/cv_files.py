from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.core.config import get_settings


MAX_CV_BYTES = 10 * 1024 * 1024
ALLOWED_SUFFIXES = {".pdf", ".docx"}


def cv_storage_dir() -> Path:
    configured = get_settings().upload_dir
    directory = configured if configured.is_absolute() else Path(__file__).resolve().parents[2] / configured
    directory.mkdir(parents=True, exist_ok=True)
    return directory.resolve()


def private_company_docs_dir() -> Path:
    directory = cv_storage_dir() / "company-documents"
    directory.mkdir(parents=True, exist_ok=True)
    return directory.resolve()


def clean_original_name(name: str | None) -> str:
    raw = (name or "cv").replace("\\", "/").split("/")[-1]
    safe = "".join(char for char in raw if char.isprintable() and char not in "<>:\"|?*").strip()
    return safe[:255] or "cv"


async def read_and_validate_cv(upload: UploadFile) -> tuple[bytes, str, str]:
    original_name = clean_original_name(upload.filename)
    suffix = Path(original_name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=415, detail="Chỉ chấp nhận CV định dạng PDF hoặc DOCX")

    content = await upload.read(MAX_CV_BYTES + 1)
    if len(content) > MAX_CV_BYTES:
        raise HTTPException(status_code=413, detail="CV không được vượt quá 10 MB")
    if not content:
        raise HTTPException(status_code=400, detail="Tệp tải lên đang trống")

    if suffix == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise HTTPException(status_code=415, detail="Nội dung tệp không đúng định dạng PDF")
        media_type = "application/pdf"
    else:
        if not content.startswith(b"PK"):
            raise HTTPException(status_code=415, detail="Nội dung tệp không đúng định dạng DOCX")
        try:
            from io import BytesIO
            from zipfile import BadZipFile, ZipFile

            with ZipFile(BytesIO(content)) as archive:
                names = set(archive.namelist())
                total_uncompressed = sum(item.file_size for item in archive.infolist())
                if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                    raise ValueError("not a Word document")
                if len(names) > 1000 or total_uncompressed > 50 * 1024 * 1024:
                    raise ValueError("document archive exceeds limits")
        except (BadZipFile, ValueError) as exc:
            raise HTTPException(status_code=415, detail="Tệp không phải tài liệu DOCX hợp lệ") from exc
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    return content, original_name, media_type


def store_cv(content: bytes, suffix: str) -> str:
    storage_name = f"{uuid4().hex}{suffix}"
    destination = cv_storage_dir() / storage_name
    destination.write_bytes(content)
    return storage_name


def delete_cv_file(storage_name: str) -> None:
    directory = cv_storage_dir()
    target = (directory / storage_name).resolve()
    if target.parent != directory:
        raise ValueError("Invalid CV storage key")
    target.unlink(missing_ok=True)
