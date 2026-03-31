"""Drop unused indexes: anime_link on cards/decks, collection on card_users_stats

Revision ID: b2c3d4e5f6a7
Revises: a7b9c1d2e3f4
Create Date: 2026-03-31 12:00:00.000000

"""

from typing import Sequence, Union
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a7b9c1d2e3f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_animestars_cards_anime_link", table_name="animestars_cards", if_exists=True)
    op.drop_index("ix_animestars_decks_anime_link", table_name="animestars_decks", if_exists=True)
    op.drop_index("ix_animestars_card_users_stats_collection", table_name="animestars_card_users_stats", if_exists=True)


def downgrade() -> None:
    op.create_index("ix_animestars_card_users_stats_collection", "animestars_card_users_stats", ["collection"])
    op.create_index("ix_animestars_cards_anime_link", "animestars_cards", ["anime_link"])
    op.create_index("ix_animestars_decks_anime_link", "animestars_decks", ["anime_link"])
