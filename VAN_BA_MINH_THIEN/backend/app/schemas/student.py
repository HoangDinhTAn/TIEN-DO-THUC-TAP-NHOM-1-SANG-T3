from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class EducationInput(BaseModel):
    school: str = Field(min_length=2, max_length=200)
    major: str = Field(min_length=2, max_length=160)
    degree: str | None = Field(default=None, max_length=100)
    start_year: int | None = Field(default=None, ge=1950, le=2100)
    end_year: int | None = Field(default=None, ge=1950, le=2100)
    gpa: float | None = Field(default=None, ge=0, le=10)
    gpa_scale: Literal[4, 10] | None = None


class SkillInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category: Literal["technical", "tool", "soft", "language"] = "technical"
    level: int = Field(default=1, ge=1, le=4)
    years: float = Field(default=0, ge=0, le=60)


class ExperienceInput(BaseModel):
    organization: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=6000)
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool = False

    @model_validator(mode="after")
    def valid_dates(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("Ngày kết thúc phải sau ngày bắt đầu")
        return self


class ProjectInput(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    role: str | None = Field(default=None, max_length=160)
    description: str = Field(default="", max_length=6000)
    technologies: list[str] = Field(default_factory=list, max_length=30)
    url: HttpUrl | None = None
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def valid_dates(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("Ngày kết thúc phải sau ngày bắt đầu")
        return self


class StudentProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=160)
    phone: str | None = Field(default=None, max_length=32)
    province: str | None = Field(default=None, max_length=100)
    bio: str | None = Field(default=None, max_length=2000)
    school: str | None = Field(default=None, max_length=200)
    faculty: str | None = Field(default=None, max_length=160)
    major: str | None = Field(default=None, max_length=160)
    gpa: float | None = Field(default=None, ge=0, le=10)
    gpa_scale: Literal[4, 10] | None = None
    enrollment_year: int | None = Field(default=None, ge=1950, le=2100)
    graduation_year: int | None = Field(default=None, ge=1950, le=2100)
    education: list[EducationInput] | None = Field(default=None, max_length=20)
    skills: list[SkillInput] | None = Field(default=None, max_length=100)
    experiences: list[ExperienceInput] | None = Field(default=None, max_length=50)
    projects: list[ProjectInput] | None = Field(default=None, max_length=50)


class PreferenceUpdate(BaseModel):
    desired_roles: list[str] = Field(default_factory=list, max_length=20)
    job_types: list[Literal["internship", "part_time", "full_time", "freelance", "remote", "hybrid"]] = Field(default_factory=list, max_length=10)
    locations: list[str] = Field(default_factory=list, max_length=30)
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    start_date: date | None = None
    remote_pref: Literal["any", "remote", "onsite", "hybrid"] = "any"

    @model_validator(mode="after")
    def salary_range_valid(self):
        if self.salary_min is not None and self.salary_max is not None and self.salary_max < self.salary_min:
            raise ValueError("Mức lương tối đa phải lớn hơn hoặc bằng mức tối thiểu")
        return self


class VisibilityUpdate(BaseModel):
    visibility: Literal["public", "invited", "hidden"]


class StudentProfileResponse(BaseModel):
    full_name: str
    email: str
    phone: str | None
    province: str | None
    bio: str | None
    school: str | None
    faculty: str | None
    major: str | None
    gpa: float | None
    gpa_scale: int | None
    enrollment_year: int | None
    graduation_year: int | None
    visibility: str
    completeness: int
    education: list[EducationInput]
    skills: list[SkillInput]
    experiences: list[ExperienceInput]
    projects: list[ProjectInput]
    model_config = ConfigDict(from_attributes=True)
