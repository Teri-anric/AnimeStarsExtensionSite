"""Store emission observations separately from labyrinth room types

Revision ID: b9c8d7e6f5a4
Revises: a8b7c6d5e4f3
Create Date: 2026-07-26 13:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b9c8d7e6f5a4"
down_revision: Union[str, None] = "a8b7c6d5e4f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "extension_labyrinth_rooms",
        sa.Column("emission_event", sa.String(length=80), nullable=True),
    )
    op.add_column(
        "extension_labyrinth_rooms",
        sa.Column("emission_sources_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "extension_labyrinth_rooms",
        sa.Column("emission_observed_at", sa.DateTime(), nullable=True),
    )
    op.alter_column("extension_labyrinth_rooms", "emission_sources_count", server_default=None)


def downgrade() -> None:
    op.drop_column("extension_labyrinth_rooms", "emission_observed_at")
    op.drop_column("extension_labyrinth_rooms", "emission_sources_count")
    op.drop_column("extension_labyrinth_rooms", "emission_event")
