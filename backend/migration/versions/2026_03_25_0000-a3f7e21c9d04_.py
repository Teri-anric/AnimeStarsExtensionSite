"""Add composite indexes on animestars_card_users_stats

Revision ID: a3f7e21c9d04
Revises: b8174c351419
Create Date: 2026-03-25 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a3f7e21c9d04"
down_revision: Union[str, None] = "b8174c351419"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Used by get_last_card_users_stats_bulk:
    #   SELECT DISTINCT ON (card_id, collection) ... ORDER BY card_id, collection, created_at DESC
    op.create_index(
        "ix_card_users_stats_card_collection_created",
        "animestars_card_users_stats",
        ["card_id", "collection", sa.text("created_at DESC")],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_card_users_stats_card_collection_created",
        table_name="animestars_card_users_stats",
    )
