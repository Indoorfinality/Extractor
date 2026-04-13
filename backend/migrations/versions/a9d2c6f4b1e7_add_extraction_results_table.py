"""add extraction_results table

Revision ID: a9d2c6f4b1e7
Revises: 7f3b2a1c9e04
Create Date: 2026-04-06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a9d2c6f4b1e7"
down_revision: Union[str, Sequence[str], None] = "7f3b2a1c9e04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "extraction_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("studio_id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("extracted_data", sa.JSON(), nullable=False),
        sa.Column("usage", sa.JSON(), nullable=False),
        sa.Column("raw_output", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["studio_id"], ["prompt_studios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["extraction_documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_extraction_results_id"), "extraction_results", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_extraction_results_id"), table_name="extraction_results")
    op.drop_table("extraction_results")
