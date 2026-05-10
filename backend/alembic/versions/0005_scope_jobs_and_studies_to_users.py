"""Scope jobs and studies to users

Revision ID: 0005_scope_jobs_and_studies_to_users
Revises: 0004_add_documents_table
Create Date: 2026-05-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0005_scope_jobs_and_studies_to_users"
down_revision: Union[str, None] = "0004_add_documents_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_jobs_user_id"), "jobs", ["user_id"], unique=False)
    op.create_foreign_key("fk_jobs_user_id_users", "jobs", "users", ["user_id"], ["id"])

    op.add_column("studies", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_studies_user_id"), "studies", ["user_id"], unique=False)
    op.create_foreign_key("fk_studies_user_id_users", "studies", "users", ["user_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_studies_user_id_users", "studies", type_="foreignkey")
    op.drop_index(op.f("ix_studies_user_id"), table_name="studies")
    op.drop_column("studies", "user_id")

    op.drop_constraint("fk_jobs_user_id_users", "jobs", type_="foreignkey")
    op.drop_index(op.f("ix_jobs_user_id"), table_name="jobs")
    op.drop_column("jobs", "user_id")
