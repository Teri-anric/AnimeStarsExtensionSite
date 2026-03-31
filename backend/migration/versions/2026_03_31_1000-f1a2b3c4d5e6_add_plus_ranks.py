"""Add S+, A+, B+, C+, D+, E+ rank values to cardtype enum

Revision ID: f1a2b3c4d5e6
Revises: e5f6a7b8c9d0
Create Date: 2026-03-31 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# New rank values ordered directly above their base rank so that
# enum ordering (used when sorting by rank) stays logical:
# ASS > S_PLUS > S > A_PLUS > A > B_PLUS > B > C_PLUS > C > D_PLUS > D > E_PLUS > E
_NEW_RANKS = [
    ("S_PLUS", "S"),
    ("A_PLUS", "A"),
    ("B_PLUS", "B"),
    ("C_PLUS", "C"),
    ("D_PLUS", "D"),
    ("E_PLUS", "E"),
]


def upgrade() -> None:
    for value, before in _NEW_RANKS:
        op.execute(
            f"ALTER TYPE cardtype ADD VALUE IF NOT EXISTS '{value}' BEFORE '{before}'"
        )


def downgrade() -> None:
    # PostgreSQL does not support removing individual enum values.
    # A full recreate-and-cast approach would be needed; skipping for safety.
    pass
