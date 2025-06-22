"""empty message

Revision ID: 589915f041c5
Revises: f2c712c9582f
Create Date: 2025-06-22 13:23:27.126294

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "589915f041c5"
down_revision: Union[str, None] = "f2c712c9582f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_CARD_COLLECTION_ENUM = sa.Enum("TRADE", "NEED", "OWNED", name="card_collection")
CARD_STATS_STATE_ENUM = sa.Enum("LOCKED", "UNLOCKED", name="card_stats_state")

OLD_CARD_COLLECTION_ENUM = sa.Enum("TRADE", "NEED", "OWNED", name="cardcollection")
OLD_CARD_STATE_ENUM = sa.Enum("LOCKED", "UNLOCKED", name="summarycardstate")


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(
        "ix_animestars_summary_card_users_card_id",
        table_name="animestars_card_users_stats",
    )
    op.drop_index(
        "ix_animestars_summary_card_users_collection",
        table_name="animestars_card_users_stats",
    )
    op.drop_table("animestars_summary_card_users")
    bind = op.get_bind()
    OLD_CARD_COLLECTION_ENUM.drop(bind=bind, checkfirst=True)
    OLD_CARD_STATE_ENUM.drop(bind=bind, checkfirst=True)

    op.create_table(
        "animestars_card_users_stats",
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column(
            "collection",
            NEW_CARD_COLLECTION_ENUM,
            nullable=False,
        ),
        sa.Column(
            "state",
            CARD_STATS_STATE_ENUM,
            nullable=False,
        ),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["card_id"],
            ["animestars_cards.card_id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_animestars_card_users_stats_card_id"),
        "animestars_card_users_stats",
        ["card_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_animestars_card_users_stats_collection"),
        "animestars_card_users_stats",
        ["collection"],
        unique=False,
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_animestars_card_users_stats_collection"),
        table_name="animestars_card_users_stats",
    )
    op.drop_index(
        op.f("ix_animestars_card_users_stats_card_id"),
        table_name="animestars_card_users_stats",
    )
    op.drop_table("animestars_card_users_stats")
    bind = op.get_bind()
    NEW_CARD_COLLECTION_ENUM.drop(bind=bind, checkfirst=True)
    CARD_STATS_STATE_ENUM.drop(bind=bind, checkfirst=True)

    op.create_table(
        "animestars_summary_card_users",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            "card_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "collection",
            OLD_CARD_COLLECTION_ENUM,
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "state",
            OLD_CARD_STATE_ENUM,
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("count", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["card_id"],
            ["animestars_cards.card_id"],
            name="animestars_summary_card_users_card_id_fkey",
        ),
        sa.PrimaryKeyConstraint(
            "id", name="animestars_summary_card_users_pkey"
        ),
    )
    op.create_index(
        "ix_animestars_summary_card_users_collection",
        "animestars_summary_card_users",
        ["collection"],
        unique=False,
    )
    op.create_index(
        "ix_animestars_summary_card_users_card_id",
        "animestars_summary_card_users",
        ["card_id"],
        unique=False,
    )
