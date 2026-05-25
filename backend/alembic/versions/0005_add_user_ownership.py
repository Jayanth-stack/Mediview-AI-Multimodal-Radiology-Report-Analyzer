"""Add user ownership for jobs and studies

Revision ID: 0005_add_user_ownership
Revises: 0004_add_documents_table
Create Date: 2026-05-25

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0005_add_user_ownership"
down_revision: Union[str, None] = "0004_add_documents_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE IF EXISTS studies ADD COLUMN IF NOT EXISTS user_id INTEGER")
    op.execute("ALTER TABLE IF EXISTS jobs ADD COLUMN IF NOT EXISTS user_id INTEGER")
    op.execute("CREATE INDEX IF NOT EXISTS ix_studies_user_id ON studies (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_jobs_user_id ON jobs (user_id)")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_studies_user_id_users'
            ) THEN
                ALTER TABLE studies
                ADD CONSTRAINT fk_studies_user_id_users
                FOREIGN KEY (user_id) REFERENCES users (id);
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_jobs_user_id_users'
            ) THEN
                ALTER TABLE jobs
                ADD CONSTRAINT fk_jobs_user_id_users
                FOREIGN KEY (user_id) REFERENCES users (id);
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE IF EXISTS jobs DROP CONSTRAINT IF EXISTS fk_jobs_user_id_users")
    op.execute("ALTER TABLE IF EXISTS studies DROP CONSTRAINT IF EXISTS fk_studies_user_id_users")
    op.execute("DROP INDEX IF EXISTS ix_jobs_user_id")
    op.execute("DROP INDEX IF EXISTS ix_studies_user_id")
    op.execute("ALTER TABLE IF EXISTS jobs DROP COLUMN IF EXISTS user_id")
    op.execute("ALTER TABLE IF EXISTS studies DROP COLUMN IF EXISTS user_id")
