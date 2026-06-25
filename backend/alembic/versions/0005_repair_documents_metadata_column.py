"""Repair documents metadata column rename

Revision ID: 0005_repair_documents_metadata_column
Revises: 0004_add_documents_table
Create Date: 2026-06-25

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0005_repair_documents_metadata_column"
down_revision: Union[str, None] = "0004_add_documents_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'documents' AND column_name = 'metadata'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'documents' AND column_name = 'doc_metadata'
            ) THEN
                ALTER TABLE documents RENAME COLUMN metadata TO doc_metadata;
            ELSIF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'documents' AND column_name = 'metadata'
            ) AND EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'documents' AND column_name = 'doc_metadata'
            ) THEN
                UPDATE documents
                SET doc_metadata = metadata
                WHERE doc_metadata IS NULL AND metadata IS NOT NULL;
                ALTER TABLE documents DROP COLUMN metadata;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'documents' AND column_name = 'doc_metadata'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'documents' AND column_name = 'metadata'
            ) THEN
                ALTER TABLE documents RENAME COLUMN doc_metadata TO metadata;
            END IF;
        END $$;
        """
    )
