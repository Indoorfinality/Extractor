"""fix deployment endpoint urls

Revision ID: e31b6c9a4d12
Revises: d2c1b8e4f9aa
Create Date: 2026-04-08
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e31b6c9a4d12"
down_revision: Union[str, Sequence[str], None] = "d2c1b8e4f9aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE api_deployments
        SET endpoint_url = '/api/extraction/extract/' || name
        WHERE endpoint_url LIKE '/api/extract/%'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE api_deployments
        SET endpoint_url = '/api/extract/' || name
        WHERE endpoint_url LIKE '/api/extraction/extract/%'
        """
    )
