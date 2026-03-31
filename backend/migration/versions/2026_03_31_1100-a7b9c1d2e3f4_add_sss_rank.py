"""Add SSS rank value to cardtype enum

Revision ID: a7b9c1d2e3f4
Revises: f1a2b3c4d5e6
Create Date: 2026-03-31 11:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


revision: str = "a7b9c1d2e3f4"
down_revision: Union[str, None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE cardtype ADD VALUE IF NOT EXISTS 'SSS' BEFORE 'ASS'"
    )


def downgrade() -> None:
    # PostgreSQL does not support removing individual enum values.
    # A full recreate-and-cast approach would be needed; skipping for safety.
    pass
