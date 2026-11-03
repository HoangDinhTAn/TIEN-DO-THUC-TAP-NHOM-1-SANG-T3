from fastapi import APIRouter, HTTPException

from app.core.config import get_settings


router = APIRouter(prefix="/system", tags=["system"])


@router.get("/demo-accounts")
def demo_accounts():
    settings = get_settings()
    if settings.environment.lower() != "development":
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "environment": "development",
        "notice": "Tài khoản demo chỉ dành cho local testing. Chạy seed_dev để tạo chúng trong database.",
        "accounts": [
            {"role": "Platform Admin", "email": "admin@huong.local", "password": settings.seed_admin_password},
            {"role": "Sinh viên", "email": "student@huong.local", "password": settings.seed_student_password},
            {"role": "Nhà tuyển dụng", "email": "recruiter@huong.local", "password": settings.seed_recruiter_password},
        ],
    }
