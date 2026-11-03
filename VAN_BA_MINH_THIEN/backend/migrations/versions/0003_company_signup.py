"""Add company records and founding recruiter memberships.

Revision ID: 0003_company
Revises: 0002_student
"""
from alembic import op
import sqlalchemy as sa


revision = "0003_company"
down_revision = "0002_student"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("tax_code", sa.String(length=20), nullable=False),
        sa.Column("industry", sa.String(length=160)),
        sa.Column("website", sa.String(length=300)),
        sa.Column("verification_status", sa.String(length=24), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tax_code", name="uq_companies_tax_code"),
    )
    op.create_table(
        "company_members",
        sa.Column("company_id", sa.String(length=36), sa.ForeignKey("companies.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="owner"),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("company_members")
    op.drop_table("companies")
