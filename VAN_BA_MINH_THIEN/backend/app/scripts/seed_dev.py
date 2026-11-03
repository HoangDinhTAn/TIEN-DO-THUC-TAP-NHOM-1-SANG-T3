"""Create repeatable local-only demo accounts and starter profile data."""
from datetime import date, datetime, timezone

from sqlalchemy import inspect, select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
import app.models  # noqa: F401 - register model metadata
from app.models.auth import Consent, User
from app.models.company import Company, CompanyMember
from app.models.student import (
    StudentEducation,
    StudentPreference,
    StudentProfile,
    StudentProject,
    StudentSkill,
)


NOW = datetime.now(timezone.utc)
ACCOUNTS = [
    {
        "email": "admin@huong.local",
        "full_name": "Hướng Platform Admin",
        "role": "platform_admin",
        "password_setting": "seed_admin_password",
    },
    {
        "email": "student@huong.local",
        "full_name": "Nguyễn Minh Anh",
        "role": "student",
        "password_setting": "seed_student_password",
    },
    {
        "email": "recruiter@huong.local",
        "full_name": "Trần Gia Huy",
        "role": "recruiter",
        "password_setting": "seed_recruiter_password",
    },
]


def require_migrations() -> None:
    inspector = inspect(engine)
    required = {"users", "consents", "companies", "company_members", "student_profiles"}
    missing = required.difference(inspector.get_table_names())
    if missing:
        names = ", ".join(sorted(missing))
        raise SystemExit(f"Database chưa có schema ({names}). Chạy `alembic upgrade head` trước.")


def main() -> None:
    settings = get_settings()
    if settings.environment.lower() != "development":
        raise SystemExit("Seed demo chỉ được phép chạy khi ENVIRONMENT=development.")
    require_migrations()

    db = SessionLocal()
    created = []
    skipped = []
    try:
        users: dict[str, User] = {}
        for account in ACCOUNTS:
            email = account["email"]
            user = db.scalar(select(User).where(User.email == email))
            if user:
                users[account["role"]] = user
                skipped.append(email)
                continue

            password = getattr(settings, account["password_setting"])
            user = User(
                email=email,
                full_name=account["full_name"],
                password_hash=hash_password(password),
                role=account["role"],
                status="active",
                email_verified_at=NOW,
            )
            db.add(user)
            db.flush()
            db.add_all([
                Consent(user_id=user.id, purpose="terms_of_service", granted=True, policy_version="dev-seed"),
                Consent(user_id=user.id, purpose="personal_data_processing", granted=True, policy_version="dev-seed"),
            ])
            users[account["role"]] = user
            created.append(email)

        student = users.get("student")
        if student and db.get(StudentProfile, student.id) is None:
            db.add(StudentProfile(
                user_id=student.id,
                province="TP. Hồ Chí Minh",
                bio="Sinh viên Công nghệ thông tin, đang tìm cơ hội thực tập phát triển web.",
                school="Đại học Công nghệ TP. Hồ Chí Minh",
                major="Công nghệ thông tin",
                gpa=3.4,
                gpa_scale=4,
                enrollment_year=2023,
                graduation_year=2027,
                visibility="public",
            ))
            db.add(StudentPreference(
                student_id=student.id,
                desired_roles=["Frontend Developer Intern"],
                job_types=["internship"],
                locations=["TP. Hồ Chí Minh", "Remote"],
                salary_min=4000000,
                salary_max=7000000,
                start_date=date(2026, 6, 1),
                remote_pref="any",
            ))
            db.add(StudentEducation(
                student_id=student.id,
                school="Đại học Công nghệ TP. Hồ Chí Minh",
                major="Công nghệ thông tin",
                degree="Cử nhân",
                start_year=2023,
                end_year=2027,
                gpa=3.4,
                gpa_scale=4,
            ))
            for name, category, level in [
                ("React", "technical", 3),
                ("TypeScript", "technical", 2),
                ("JavaScript", "technical", 3),
                ("Git", "tool", 2),
            ]:
                db.add(StudentSkill(
                    student_id=student.id,
                    name=name,
                    normalized_name=name.casefold(),
                    category=category,
                    level=level,
                    years=1,
                ))
            db.add(StudentProject(
                student_id=student.id,
                name="Campus Connect",
                role="Frontend Developer",
                description="Prototype cộng đồng sinh viên xây bằng React và TypeScript.",
                technologies=["React", "TypeScript"],
                url="https://github.com/example/campus-connect",
            ))

        recruiter = users.get("recruiter")
        if recruiter and not db.scalar(select(CompanyMember).where(CompanyMember.user_id == recruiter.id)):
            company = Company(
                name="Mây Studio (Demo)",
                tax_code="9900000001",
                industry="Công nghệ thông tin",
                website="https://example.com",
                verification_status="pending",
            )
            db.add(company)
            db.flush()
            db.add(CompanyMember(company_id=company.id, user_id=recruiter.id, role="owner", title="Recruiter"))

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print("Demo seed complete.")
    for account in ACCOUNTS:
        print(f"{account['role']}: {account['email']} (password: {getattr(settings, account['password_setting'])})")
    if created:
        print(f"Created: {', '.join(created)}")
    if skipped:
        print(f"Already existed (credentials unchanged): {', '.join(skipped)}")


if __name__ == "__main__":
    main()
