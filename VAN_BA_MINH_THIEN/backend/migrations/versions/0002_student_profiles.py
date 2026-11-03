"""Add student profile, preferences, skills, education, experience and projects.

Revision ID: 0002_student
Revises: 0001_auth
"""
from alembic import op
import sqlalchemy as sa


revision = "0002_student"
down_revision = "0001_auth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "student_profiles",
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("phone", sa.String(length=32)),
        sa.Column("province", sa.String(length=100)),
        sa.Column("bio", sa.Text()),
        sa.Column("school", sa.String(length=200)),
        sa.Column("faculty", sa.String(length=160)),
        sa.Column("major", sa.String(length=160)),
        sa.Column("gpa", sa.Float()),
        sa.Column("gpa_scale", sa.Integer()),
        sa.Column("enrollment_year", sa.Integer()),
        sa.Column("graduation_year", sa.Integer()),
        sa.Column("visibility", sa.String(length=24), nullable=False, server_default="hidden"),
        sa.Column("job_search_status", sa.String(length=24), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "student_preferences",
        sa.Column("student_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("desired_roles", sa.JSON(), nullable=False),
        sa.Column("job_types", sa.JSON(), nullable=False),
        sa.Column("locations", sa.JSON(), nullable=False),
        sa.Column("salary_min", sa.Integer()),
        sa.Column("salary_max", sa.Integer()),
        sa.Column("start_date", sa.Date()),
        sa.Column("remote_pref", sa.String(length=24), nullable=False, server_default="any"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "student_educations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("student_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("school", sa.String(length=200), nullable=False),
        sa.Column("major", sa.String(length=160), nullable=False),
        sa.Column("degree", sa.String(length=100)),
        sa.Column("start_year", sa.Integer()),
        sa.Column("end_year", sa.Integer()),
        sa.Column("gpa", sa.Float()),
        sa.Column("gpa_scale", sa.Integer()),
    )
    op.create_index("ix_student_educations_student_id", "student_educations", ["student_id"])
    op.create_table(
        "student_skills",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("student_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("normalized_name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False, server_default="technical"),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("years", sa.Float(), nullable=False, server_default="0"),
    )
    op.create_index("ix_student_skills_student_id", "student_skills", ["student_id"])
    op.create_index("ix_student_skills_normalized_name", "student_skills", ["normalized_name"])
    op.create_table(
        "student_experiences",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("student_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization", sa.String(length=200), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_student_experiences_student_id", "student_experiences", ["student_id"])
    op.create_table(
        "student_projects",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("student_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("role", sa.String(length=160)),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("technologies", sa.JSON(), nullable=False),
        sa.Column("url", sa.String(length=500)),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
    )
    op.create_index("ix_student_projects_student_id", "student_projects", ["student_id"])


def downgrade() -> None:
    op.drop_index("ix_student_projects_student_id", table_name="student_projects")
    op.drop_table("student_projects")
    op.drop_index("ix_student_experiences_student_id", table_name="student_experiences")
    op.drop_table("student_experiences")
    op.drop_index("ix_student_skills_normalized_name", table_name="student_skills")
    op.drop_index("ix_student_skills_student_id", table_name="student_skills")
    op.drop_table("student_skills")
    op.drop_index("ix_student_educations_student_id", table_name="student_educations")
    op.drop_table("student_educations")
    op.drop_table("student_preferences")
    op.drop_table("student_profiles")
