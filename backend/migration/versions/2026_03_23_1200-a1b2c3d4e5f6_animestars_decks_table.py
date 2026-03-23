"""Add animestars_decks table and card.deck_id

Revision ID: a1b2c3d4e5f6
Revises: b8174c351419
Create Date: 2026-03-23 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "b8174c351419"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "animestars_decks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("anime_name", sa.String(), nullable=False),
        sa.Column("anime_link", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("uq_animestars_decks_anime_name"),
        "animestars_decks",
        ["anime_name"],
        unique=True,
    )
    op.create_index(
        op.f("ix_animestars_decks_anime_link"),
        "animestars_decks",
        ["anime_link"],
        unique=False,
    )
    op.add_column(
        "animestars_cards",
        sa.Column("deck_id", sa.UUID(), nullable=True),
    )
    op.create_index(
        op.f("ix_animestars_cards_deck_id"),
        "animestars_cards",
        ["deck_id"],
        unique=False,
    )
    op.create_foreign_key(
        op.f("fk_animestars_cards_deck_id_animestars_decks"),
        "animestars_cards",
        "animestars_decks",
        ["deck_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # One deck per canonical key: trimmed name, else trimmed link (matches canonical_deck_key in Python).
    op.execute(
        sa.text(
            """
            INSERT INTO animestars_decks (id, anime_name, anime_link, created_at, updated_at)
            SELECT gen_random_uuid(),
                   dk.deck_key,
                   MAX(dk.link_part),
                   NOW(),
                   NOW()
            FROM (
                SELECT
                    COALESCE(
                        NULLIF(TRIM(COALESCE(anime_name, '')), ''),
                        NULLIF(TRIM(COALESCE(anime_link, '')), '')
                    ) AS deck_key,
                    NULLIF(TRIM(COALESCE(anime_link, '')), '') AS link_part
                FROM animestars_cards
            ) AS dk
            WHERE dk.deck_key IS NOT NULL
            GROUP BY dk.deck_key
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE animestars_cards AS c
            SET deck_id = d.id
            FROM animestars_decks AS d
            WHERE COALESCE(
                NULLIF(TRIM(COALESCE(c.anime_name, '')), ''),
                NULLIF(TRIM(COALESCE(c.anime_link, '')), '')
            ) = d.anime_name
            """
        )
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_animestars_cards_deck_id_animestars_decks"),
        "animestars_cards",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_animestars_cards_deck_id"), table_name="animestars_cards")
    op.drop_column("animestars_cards", "deck_id")
    op.drop_index(op.f("ix_animestars_decks_anime_link"), table_name="animestars_decks")
    op.drop_index(
        op.f("uq_animestars_decks_anime_name"), table_name="animestars_decks"
    )
    op.drop_table("animestars_decks")
