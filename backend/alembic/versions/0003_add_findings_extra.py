"""
phase3: add findings.extra json column

Revision ID: 0003_add_findings_extra
Revises: 0002_add_columns_after_table_create
Create Date: 2025-08-11 00:20:00
"""
from alembic import op
import sqlalchemy as sa


revision = "0003_add_findings_extra"
down_revision = "0002_add_columns_after_table_create"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE IF EXISTS findings ADD COLUMN IF NOT EXISTS extra JSONB")


def downgrade() -> None:
    op.execute("ALTER TABLE IF EXISTS findings DROP COLUMN IF EXISTS extra")


