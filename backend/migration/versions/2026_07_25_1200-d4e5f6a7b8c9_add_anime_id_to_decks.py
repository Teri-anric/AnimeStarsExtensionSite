"""Add source anime ids to decks

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-25 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("animestars_decks", sa.Column("anime_id", sa.Integer(), nullable=True))
    op.execute(
        sa.text(
            """
            UPDATE animestars_decks
            SET anime_id = (regexp_match(anime_link, '/(\\d+)-[^/]+(?:\\.html)?/?$'))[1]::integer
            WHERE anime_link ~ '/\\d+-[^/]+(?:\\.html)?/?$'
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE animestars_decks AS d
            SET anime_id = source.anime_id
            FROM (
                SELECT c.deck_id,
                       min((regexp_match(c.anime_link, '/(\\d+)-[^/]+(?:\\.html)?/?$'))[1]::integer) AS anime_id
                FROM animestars_cards AS c
                WHERE c.deck_id IS NOT NULL
                  AND c.anime_link ~ '/\\d+-[^/]+(?:\\.html)?/?$'
                GROUP BY c.deck_id
            ) AS source
            WHERE d.id = source.deck_id AND d.anime_id IS NULL
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE animestars_cards
            SET deck_id = NULL
            WHERE deck_id IN (SELECT id FROM animestars_decks WHERE anime_id IS NULL)
            """
        )
    )
    op.execute(sa.text("DELETE FROM animestars_decks WHERE anime_id IS NULL"))
    op.execute(
        sa.text(
            """
            WITH duplicate_decks AS (
                SELECT anime_id, min(id::text)::uuid AS keep_id
                FROM animestars_decks
                GROUP BY anime_id
                HAVING count(*) > 1
            )
            UPDATE animestars_cards AS c
            SET deck_id = d.keep_id
            FROM animestars_decks AS old_deck
            JOIN duplicate_decks AS d ON d.anime_id = old_deck.anime_id
            WHERE c.deck_id = old_deck.id AND c.deck_id <> d.keep_id
            """
        )
    )
    op.execute(
        sa.text(
            """
            DELETE FROM animestars_decks AS old_deck
            USING (
                SELECT anime_id, min(id::text)::uuid AS keep_id
                FROM animestars_decks
                GROUP BY anime_id
                HAVING count(*) > 1
            ) AS duplicates
            WHERE old_deck.anime_id = duplicates.anime_id AND old_deck.id <> duplicates.keep_id
            """
        )
    )
    op.create_index(
        "uq_animestars_decks_anime_id",
        "animestars_decks",
        ["anime_id"],
        unique=True,
    )
    op.alter_column("animestars_decks", "anime_id", nullable=False)


def downgrade() -> None:
    op.drop_index("uq_animestars_decks_anime_id", table_name="animestars_decks")
    op.drop_column("animestars_decks", "anime_id")
