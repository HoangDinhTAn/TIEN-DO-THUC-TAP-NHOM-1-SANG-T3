"""Add private student CV file metadata.

Revision ID: 0004_student_cvs
Revises: 0003_company
"""
from alembic import op
import sqlalchemy as sa


revision = "0004_student_cvs"
down_revision = "0003_company"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "student_cvs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("student_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("storage_name", sa.String(length=80), nullable=False),
        sa.Column("media_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("parse_status", sa.String(length=24), nullable=False, server_default="not_parsed"),
        sa.Column("parsed_json", sa.JSON()),
        sa.Column("extracted_text", sa.Text()),
        sa.Column("parse_error", sa.String(length=300)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("storage_name", name="uq_student_cvs_storage_name"),
    )
    op.create_index("ix_student_cvs_student_id", "student_cvs", ["student_id"])


def downgrade() -> None:
    op.drop_index("ix_student_cvs_student_id", table_name="student_cvs")
    op.drop_table("student_cvs")
