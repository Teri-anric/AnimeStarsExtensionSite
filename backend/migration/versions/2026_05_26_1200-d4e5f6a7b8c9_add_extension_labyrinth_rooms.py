"""Add extension_labyrinth_rooms table

Revision ID: a8b7c6d5e4f3
Revises: c3d4e5f6a7b8
Create Date: 2026-05-26 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a8b7c6d5e4f3"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "extension_labyrinth_rooms",
        sa.Column("x", sa.Integer(), nullable=False),
        sa.Column("y", sa.Integer(), nullable=False),
        sa.Column("event", sa.String(length=80), nullable=True),
        sa.Column("sources_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("x", "y", name="uq_extension_labyrinth_rooms_xy"),
    )
    op.create_index(
        "ix_extension_labyrinth_rooms_x",
        "extension_labyrinth_rooms",
        ["x"],
    )
    op.create_index(
        "ix_extension_labyrinth_rooms_y",
        "extension_labyrinth_rooms",
        ["y"],
    )


def downgrade() -> None:
    op.drop_index("ix_extension_labyrinth_rooms_y", table_name="extension_labyrinth_rooms")
    op.drop_index("ix_extension_labyrinth_rooms_x", table_name="extension_labyrinth_rooms")
    op.drop_table("extension_labyrinth_rooms")
