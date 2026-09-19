"""Add user ownership to jobs and studies

Revision ID: 0005_add_user_ownership
Revises: 0004_add_documents_table
Create Date: 2026-07-12
"""
from typing import Sequence, Union

from alembic import op


revision: str = "0005_add_user_ownership"
down_revision: Union[str, None] = "0004_add_documents_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE IF EXISTS jobs "
        "ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE SET NULL"
    )
    op.execute(
        "ALTER TABLE IF EXISTS studies "
        "ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE SET NULL"
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_jobs_user_id ON jobs (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_studies_user_id ON studies (user_id)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_studies_user_id")
    op.execute("DROP INDEX IF EXISTS ix_jobs_user_id")
    op.execute("ALTER TABLE IF EXISTS studies DROP COLUMN IF EXISTS user_id")
    op.execute("ALTER TABLE IF EXISTS jobs DROP COLUMN IF EXISTS user_id")
