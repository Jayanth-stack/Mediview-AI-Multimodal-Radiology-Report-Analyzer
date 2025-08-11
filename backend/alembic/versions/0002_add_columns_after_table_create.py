"""
phase3: ensure new columns exist after initial table creation

Revision ID: 0002_add_columns_after_table_create
Revises: 0001_phase3_fields
Create Date: 2025-08-11 00:10:00
"""
from alembic import op
import sqlalchemy as sa


revision = "0002_add_columns_after_table_create"
down_revision = "0001_phase3_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE IF EXISTS studies ADD COLUMN IF NOT EXISTS source VARCHAR(128) DEFAULT 'upload'")
    op.execute("ALTER TABLE IF EXISTS studies ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW()")
    op.execute("ALTER TABLE IF EXISTS studies ADD COLUMN IF NOT EXISTS patient_context VARCHAR(4000)")

    op.execute("ALTER TABLE IF EXISTS reports ADD COLUMN IF NOT EXISTS summary_model VARCHAR(128)")

    op.execute("ALTER TABLE IF EXISTS findings ADD COLUMN IF NOT EXISTS model_name VARCHAR(128)")
    op.execute("ALTER TABLE IF EXISTS findings ADD COLUMN IF NOT EXISTS model_version VARCHAR(128)")


def downgrade() -> None:
    op.execute("ALTER TABLE IF EXISTS findings DROP COLUMN IF EXISTS model_version")
    op.execute("ALTER TABLE IF EXISTS findings DROP COLUMN IF EXISTS model_name")
    op.execute("ALTER TABLE IF EXISTS reports DROP COLUMN IF EXISTS summary_model")
    op.execute("ALTER TABLE IF EXISTS studies DROP COLUMN IF EXISTS patient_context")
    op.execute("ALTER TABLE IF EXISTS studies DROP COLUMN IF EXISTS created_at")
    op.execute("ALTER TABLE IF EXISTS studies DROP COLUMN IF EXISTS source")


