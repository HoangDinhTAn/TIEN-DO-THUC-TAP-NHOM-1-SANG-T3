from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Huong API"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://huong:huong_dev@localhost:5432/huong"
    jwt_secret: str = "development-only-change-before-deploy"
    access_token_minutes: int = 15
    refresh_token_days: int = 14
    verification_token_minutes: int = 15
    email_from: str = "no-reply@huong.local"
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    seed_admin_password: str = "AdminDemo2026!"
    seed_student_password: str = "StudentDemo2026!"
    seed_recruiter_password: str = "RecruiterDemo2026!"
    upload_dir: Path = Path("storage")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def require_secret_outside_development(self):
        if self.environment.lower() not in {"development", "test"} and self.jwt_secret == "development-only-change-before-deploy":
            raise ValueError("JWT_SECRET must be set to a strong secret outside development")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
