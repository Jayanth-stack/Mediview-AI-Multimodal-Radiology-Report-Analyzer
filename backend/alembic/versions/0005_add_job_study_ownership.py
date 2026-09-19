"""Add owner columns to jobs and studies.

Revision ID: 0005_job_study_ownership
Revises: 0004_add_documents_table
Create Date: 2026-06-24
"""
from alembic import op


revision = "0005_job_study_ownership"
down_revision = "0004_add_documents_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE IF EXISTS jobs ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)")
    op.execute("ALTER TABLE IF EXISTS studies ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_jobs_user_id ON jobs (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_studies_user_id ON studies (user_id)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_studies_user_id")
    op.execute("DROP INDEX IF EXISTS ix_jobs_user_id")
    op.execute("ALTER TABLE IF EXISTS studies DROP COLUMN IF EXISTS user_id")
    op.execute("ALTER TABLE IF EXISTS jobs DROP COLUMN IF EXISTS user_id")
