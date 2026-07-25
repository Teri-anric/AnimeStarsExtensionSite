"""Merge labyrinth and deck migration heads

Revision ID: c8d7e6f5a4b3
Revises: d4e5f6a7b8c9, b9c8d7e6f5a4
Create Date: 2026-07-26 14:00:00.000000

"""

from typing import Sequence, Union


revision: str = "c8d7e6f5a4b3"
down_revision: Union[str, Sequence[str], None] = ("d4e5f6a7b8c9", "b9c8d7e6f5a4")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
