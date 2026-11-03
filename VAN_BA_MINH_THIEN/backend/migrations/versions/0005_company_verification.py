"""Add company review metadata and private verification files.

Revision ID: 0005_company_verification
Revises: 0004_student_cvs
"""
from alembic import op
import sqlalchemy as sa


revision = "0005_company_verification"
down_revision = "0004_student_cvs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("companies", sa.Column("description", sa.Text()))
    op.add_column("companies", sa.Column("verification_note", sa.String(length=1000)))
    op.add_column("companies", sa.Column("verified_at", sa.DateTime(timezone=True)))
    op.add_column("companies", sa.Column("reviewed_at", sa.DateTime(timezone=True)))
    op.add_column("companies", sa.Column("reviewed_by", sa.String(length=36), sa.ForeignKey("users.id", ondelete="SET NULL")))
    op.create_table(
        "company_documents",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("company_id", sa.String(length=36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("uploaded_by", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("storage_name", sa.String(length=80), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("document_type", sa.String(length=40), nullable=False, server_default="business_registration"),
        sa.Column("media_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("storage_name", name="uq_company_documents_storage_name"),
    )
    op.create_index("ix_company_documents_company_id", "company_documents", ["company_id"])


def downgrade() -> None:
    op.drop_index("ix_company_documents_company_id", table_name="company_documents")
    op.drop_table("company_documents")
    op.drop_column("companies", "reviewed_by")
    op.drop_column("companies", "reviewed_at")
    op.drop_column("companies", "verified_at")
    op.drop_column("companies", "verification_note")
    op.drop_column("companies", "description")
