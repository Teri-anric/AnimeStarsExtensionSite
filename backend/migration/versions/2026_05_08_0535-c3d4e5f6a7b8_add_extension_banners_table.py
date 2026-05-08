"""Add extension_banners table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-08 05:35:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "extension_banners",
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("action_text", sa.String(length=80), nullable=True),
        sa.Column("action_url", sa.String(length=512), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO extension_banners (id, title, message, action_text, action_url, is_active, created_at, updated_at)
            VALUES (
                gen_random_uuid(),
                'AnimeStars Extension',
                'Latest extension update is available now.',
                NULL,
                NULL,
                FALSE,
                NOW(),
                NOW()
            )
            """
        )
    )


def downgrade() -> None:
    op.drop_table("extension_banners")
