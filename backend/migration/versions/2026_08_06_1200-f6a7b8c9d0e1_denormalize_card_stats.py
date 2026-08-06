"""Denormalize current card statistics."""

from alembic import op
import sqlalchemy as sa

revision = "f6a7b8c9d0e1"
down_revision = "e7f8a9b0c1d2"
branch_labels = None
depends_on = None


_COLLECTION_FIELDS = (
    ("trade", "TRADE"),
    ("need", "NEED"),
    ("owned", "OWNED"),
    ("unlocked_owned", "UNLOCKED_OWNED"),
)


def upgrade() -> None:
    for prefix, _ in _COLLECTION_FIELDS:
        op.add_column(
            "animestars_cards",
            sa.Column(f"{prefix}_count", sa.Integer(), nullable=True),
        )
        op.add_column(
            "animestars_cards",
            sa.Column(f"{prefix}_updated_at", sa.DateTime(), nullable=True),
        )
        op.create_index(
            f"ix_animestars_cards_{prefix}_count",
            "animestars_cards",
            [f"{prefix}_count"],
        )

    for prefix, collection in _COLLECTION_FIELDS:
        op.execute(sa.text(f"""
            UPDATE animestars_cards AS cards
            SET {prefix}_count = (
                    SELECT stats.count
                    FROM animestars_card_users_stats AS stats
                    WHERE stats.card_id = cards.card_id
                      AND stats.collection = CAST(:collection AS card_collection)
                    ORDER BY stats.created_at DESC, stats.updated_at DESC, stats.id DESC
                    LIMIT 1
                ),
                {prefix}_updated_at = (
                    SELECT stats.created_at
                    FROM animestars_card_users_stats AS stats
                    WHERE stats.card_id = cards.card_id
                      AND stats.collection = CAST(:collection AS card_collection)
                    ORDER BY stats.created_at DESC, stats.updated_at DESC, stats.id DESC
                    LIMIT 1
                )
        """).bindparams(collection=collection))


def downgrade() -> None:
    for prefix, _ in reversed(_COLLECTION_FIELDS):
        op.drop_index(
            f"ix_animestars_cards_{prefix}_count", table_name="animestars_cards"
        )
        op.drop_column("animestars_cards", f"{prefix}_updated_at")
        op.drop_column("animestars_cards", f"{prefix}_count")
