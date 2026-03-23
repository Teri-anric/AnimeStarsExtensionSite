"""Index animestars_cards.anime_link

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2026-03-23 14:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


revision: str = "b2c3d4e5f6a1"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        op.f("ix_animestars_cards_anime_link"),
        "animestars_cards",
        ["anime_link"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_animestars_cards_anime_link"),
        table_name="animestars_cards",
    )
