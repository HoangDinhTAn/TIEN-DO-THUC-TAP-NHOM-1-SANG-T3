from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.auth import User
from app.models.student import (
    StudentEducation,
    StudentExperience,
    StudentPreference,
    StudentProfile,
    StudentProject,
    StudentSkill,
)
from app.schemas.student import (
    EducationInput,
    ExperienceInput,
    PreferenceUpdate,
    ProjectInput,
    SkillInput,
    StudentProfileResponse,
    StudentProfileUpdate,
    VisibilityUpdate,
)


router = APIRouter(prefix="/students/me", tags=["student profile"])


def require_student(user: User = Depends(get_current_user)) -> User:
    if user.role != "student":
        raise HTTPException(status_code=403, detail="Chức năng này chỉ dành cho tài khoản sinh viên")
    return user


def get_or_create_profile(db: Session, user_id: str) -> StudentProfile:
    profile = db.get(StudentProfile, user_id)
    if profile is None:
        profile = StudentProfile(user_id=user_id)
        db.add(profile)
        db.flush()
    return profile


def get_or_create_preferences(db: Session, user_id: str) -> StudentPreference:
    preferences = db.get(StudentPreference, user_id)
    if preferences is None:
        preferences = StudentPreference(student_id=user_id)
        db.add(preferences)
        db.flush()
    return preferences


def profile_completeness(profile, user, education, skills, experiences, projects, preferences) -> int:
    checks = [
        bool(user.full_name and profile.bio and profile.province),
        bool(profile.school and profile.major) or bool(education),
        bool(skills),
        bool(experiences),
        bool(projects),
        bool(preferences.desired_roles and preferences.job_types and preferences.locations),
    ]
    return round(sum(checks) * 100 / len(checks))


def build_profile_response(db: Session, user: User, profile: StudentProfile) -> StudentProfileResponse:
    education = list(db.scalars(select(StudentEducation).where(StudentEducation.student_id == user.id)))
    skills = list(db.scalars(select(StudentSkill).where(StudentSkill.student_id == user.id)))
    experiences = list(db.scalars(select(StudentExperience).where(StudentExperience.student_id == user.id)))
    projects = list(db.scalars(select(StudentProject).where(StudentProject.student_id == user.id)))
    preferences = get_or_create_preferences(db, user.id)
    db.commit()
    return StudentProfileResponse(
        full_name=user.full_name,
        email=user.email,
        phone=profile.phone,
        province=profile.province,
        bio=profile.bio,
        school=profile.school,
        faculty=profile.faculty,
        major=profile.major,
        gpa=profile.gpa,
        gpa_scale=profile.gpa_scale,
        enrollment_year=profile.enrollment_year,
        graduation_year=profile.graduation_year,
        visibility=profile.visibility,
        completeness=profile_completeness(profile, user, education, skills, experiences, projects, preferences),
        education=[EducationInput.model_validate(item, from_attributes=True) for item in education],
        skills=[SkillInput.model_validate(item, from_attributes=True) for item in skills],
        experiences=[ExperienceInput.model_validate(item, from_attributes=True) for item in experiences],
        projects=[ProjectInput.model_validate(item, from_attributes=True) for item in projects],
    )


@router.get("/profile", response_model=StudentProfileResponse)
def read_profile(user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = get_or_create_profile(db, user.id)
    return build_profile_response(db, user, profile)


@router.patch("/profile", response_model=StudentProfileResponse)
def update_profile(
    payload: StudentProfileUpdate,
    user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    profile = get_or_create_profile(db, user.id)
    values = payload.model_dump(exclude_unset=True)
    if "full_name" in values:
        user.full_name = values.pop("full_name")

    collections = {
        "education": (StudentEducation, EducationInput),
        "skills": (StudentSkill, SkillInput),
        "experiences": (StudentExperience, ExperienceInput),
        "projects": (StudentProject, ProjectInput),
    }
    collection_values = {key: values.pop(key) for key in collections if key in values}
    for key, value in values.items():
        setattr(profile, key, value)

    for name, items in collection_values.items():
        model, schema = collections[name]
        for existing in db.scalars(select(model).where(model.student_id == user.id)):
            db.delete(existing)
        for item in items or []:
            data = item.model_dump()
            if name == "skills":
                data["normalized_name"] = data["name"].strip().casefold()
            if name == "projects" and data.get("url") is not None:
                data["url"] = str(data["url"])
            db.add(model(student_id=user.id, **data))

    db.commit()
    db.refresh(profile)
    return build_profile_response(db, user, profile)


@router.get("/preferences", response_model=PreferenceUpdate)
def read_preferences(user: User = Depends(require_student), db: Session = Depends(get_db)):
    preferences = get_or_create_preferences(db, user.id)
    db.commit()
    return preferences


@router.put("/preferences", response_model=PreferenceUpdate)
def update_preferences(
    payload: PreferenceUpdate,
    user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    preferences = get_or_create_preferences(db, user.id)
    for key, value in payload.model_dump().items():
        setattr(preferences, key, value)
    db.commit()
    db.refresh(preferences)
    return preferences


@router.put("/visibility")
def update_visibility(
    payload: VisibilityUpdate,
    user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    profile = get_or_create_profile(db, user.id)
    profile.visibility = payload.visibility
    db.commit()
    return {"visibility": profile.visibility}
