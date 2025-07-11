"""add expire_at to tokens table

Revision ID: 43622a4ba80d
Revises: 66d4651d7f92
Create Date: 2025-07-11 00:46:26.279496

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "43622a4ba80d"
down_revision: Union[str, None] = "66d4651d7f92"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("tokens", sa.Column("expire_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("tokens", "expire_at")
