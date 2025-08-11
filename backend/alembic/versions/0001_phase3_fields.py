"""
phase3: add study/report/finding columns

Revision ID: 0001_phase3_fields
Revises: 
Create Date: 2025-08-11 00:00:00
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_phase3_fields"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # studies
    op.execute("ALTER TABLE IF EXISTS studies ADD COLUMN IF NOT EXISTS source VARCHAR(128) DEFAULT 'upload'")
    op.execute("ALTER TABLE IF EXISTS studies ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW()")
    op.execute("ALTER TABLE IF EXISTS studies ADD COLUMN IF NOT EXISTS patient_context VARCHAR(4000)")

    # reports
    op.execute("ALTER TABLE IF EXISTS reports ADD COLUMN IF NOT EXISTS summary_model VARCHAR(128)")

    # findings
    op.execute("ALTER TABLE IF EXISTS findings ADD COLUMN IF NOT EXISTS model_name VARCHAR(128)")
    op.execute("ALTER TABLE IF EXISTS findings ADD COLUMN IF NOT EXISTS model_version VARCHAR(128)")


def downgrade() -> None:
    # findings
    op.execute("ALTER TABLE IF EXISTS findings DROP COLUMN IF EXISTS model_version")
    op.execute("ALTER TABLE IF EXISTS findings DROP COLUMN IF EXISTS model_name")

    # reports
    op.execute("ALTER TABLE IF EXISTS reports DROP COLUMN IF EXISTS summary_model")

    # studies
    op.execute("ALTER TABLE IF EXISTS studies DROP COLUMN IF EXISTS patient_context")
    op.execute("ALTER TABLE IF EXISTS studies DROP COLUMN IF EXISTS created_at")
    op.execute("ALTER TABLE IF EXISTS studies DROP COLUMN IF EXISTS source")


