from datetime import datetime

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=20, max_length=12000)
    location: str = Field(min_length=2, max_length=160)
    employment_type: str = Field(pattern="^(internship|part_time|full_time|freelance|remote|hybrid)$")
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    skills: list[str] = Field(default_factory=list, max_length=30)


class JobResponse(BaseModel):
    id: str
    company_id: str
    company_name: str
    company_verified: bool
    title: str
    description: str
    location: str
    employment_type: str
    salary_min: int | None
    salary_max: int | None
    skills: list[str]
    status: str
    created_at: datetime


class ApplicationCreate(BaseModel):
    cv_id: str | None = None
    cover_letter: str | None = Field(default=None, max_length=5000)


class ApplicationResponse(BaseModel):
    id: str
    job_id: str
    student_id: str
    job_title: str
    company_name: str
    cv_id: str | None
    status: str
    created_at: datetime


class RecruiterApplicationResponse(BaseModel):
    id: str
    job_id: str
    job_title: str
    student_id: str
    student_name: str
    cv_id: str | None
    status: str
    created_at: datetime


class ApplicationStatusUpdate(BaseModel):
    status: str = Field(pattern="^(viewed|interview|rejected)$")
