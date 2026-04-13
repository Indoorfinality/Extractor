"""make extraction_result document_id nullable

Revision ID: f8a1d4c2b7e9
Revises: e31b6c9a4d12
Create Date: 2026-04-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f8a1d4c2b7e9"
down_revision: Union[str, Sequence[str], None] = "e31b6c9a4d12"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "extraction_results",
        "document_id",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "extraction_results",
        "document_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
