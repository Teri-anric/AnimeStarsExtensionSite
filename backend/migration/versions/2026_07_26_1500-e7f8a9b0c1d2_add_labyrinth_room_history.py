"""Add labyrinth room event history

Revision ID: e7f8a9b0c1d2
Revises: c8d7e6f5a4b3
Create Date: 2026-07-26 15:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e7f8a9b0c1d2"
down_revision: Union[str, None] = "c8d7e6f5a4b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "extension_labyrinth_room_history",
        sa.Column("room_id", sa.UUID(), nullable=False),
        sa.Column("event", sa.String(length=80), nullable=False),
        sa.Column("is_emission", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["room_id"], ["extension_labyrinth_rooms.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_extension_labyrinth_room_history_room_id",
        "extension_labyrinth_room_history",
        ["room_id"],
    )
    op.execute(
        """
        INSERT INTO extension_labyrinth_room_history (id, room_id, event, is_emission, created_at, updated_at)
        SELECT gen_random_uuid(), id, event, false, created_at, created_at
        FROM extension_labyrinth_rooms
        WHERE event IS NOT NULL AND event <> 'unknown'
        """
    )
    op.execute(
        """
        INSERT INTO extension_labyrinth_room_history (id, room_id, event, is_emission, created_at, updated_at)
        SELECT gen_random_uuid(), id, emission_event, true, emission_observed_at, emission_observed_at
        FROM extension_labyrinth_rooms
        WHERE emission_event IS NOT NULL
        """
    )
    op.alter_column("extension_labyrinth_room_history", "is_emission", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_extension_labyrinth_room_history_room_id", table_name="extension_labyrinth_room_history")
    op.drop_table("extension_labyrinth_room_history")
