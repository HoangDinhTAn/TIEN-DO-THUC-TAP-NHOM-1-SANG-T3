from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.students import router as students_router
from app.api.v1.system import router as system_router
from app.api.v1.cvs import router as cvs_router
from app.api.v1.companies import router as companies_router
from app.api.v1.admin import router as admin_router
from app.api.v1.jobs import router as jobs_router
from app.core.config import get_settings


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(students_router, prefix=settings.api_v1_prefix)
app.include_router(system_router, prefix=settings.api_v1_prefix)
app.include_router(cvs_router, prefix=settings.api_v1_prefix)
app.include_router(companies_router, prefix=settings.api_v1_prefix)
app.include_router(admin_router, prefix=settings.api_v1_prefix)
app.include_router(jobs_router, prefix=settings.api_v1_prefix)

project_root = Path(__file__).resolve().parents[2]


@app.get("/", include_in_schema=False)
def frontend_index():
    return FileResponse(project_root / "index.html")


app.mount("/src", StaticFiles(directory=project_root / "src"), name="frontend-source")
app.mount("/assets", StaticFiles(directory=project_root / "assets"), name="frontend-assets")
