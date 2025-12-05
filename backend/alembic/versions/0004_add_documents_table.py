"""Add documents table for RAG knowledge base

Revision ID: 0004_add_documents_table
Revises: 0003_add_findings_extra
Create Date: 2024-12-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0004_add_documents_table'
down_revision: Union[str, None] = '0003_add_findings_extra'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('source', sa.String(length=200), nullable=False),
        sa.Column('doc_type', sa.String(length=50), nullable=False),
        sa.Column('embedding', sa.Text(), nullable=True),  # Will be vector(768) after extension
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_index(op.f('ix_documents_title'), 'documents', ['title'], unique=False)
    op.create_index(op.f('ix_documents_source'), 'documents', ['source'], unique=False)
    op.create_index(op.f('ix_documents_doc_type'), 'documents', ['doc_type'], unique=False)
    
    # Alter embedding column to vector type
    op.execute("ALTER TABLE documents ALTER COLUMN embedding TYPE vector(768) USING embedding::vector(768)")


def downgrade() -> None:
    op.drop_index(op.f('ix_documents_doc_type'), table_name='documents')
    op.drop_index(op.f('ix_documents_source'), table_name='documents')
    op.drop_index(op.f('ix_documents_title'), table_name='documents')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')
