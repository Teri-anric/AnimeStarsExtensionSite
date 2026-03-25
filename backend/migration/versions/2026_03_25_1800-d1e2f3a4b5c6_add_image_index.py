"""Add index on animestars_cards.image

Revision ID: d1e2f3a4b5c6
Revises: a3f7e21c9d04
Create Date: 2026-03-25 18:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, None] = "a3f7e21c9d04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_animestars_cards_image", "animestars_cards", ["image"])


def downgrade() -> None:
    op.drop_index("ix_animestars_cards_image", table_name="animestars_cards")
