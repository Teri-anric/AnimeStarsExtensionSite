"""Strip host from card URL fields (image, mp4, webm, anime_link)

Revision ID: e5f6a7b8c9d0
Revises: d1e2f3a4b5c6
Create Date: 2026-03-30 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Strips scheme + host from any absolute URL, leaving only the path.
# E.g. "https://animestars.org/uploads/img.jpg" → "/uploads/img.jpg"
_STRIP_SQL = """
UPDATE animestars_cards
SET {col} = regexp_replace({col}, '^https?://[^/]+', '')
WHERE {col} ~ '^https?://'
"""


def upgrade() -> None:
    for col in ("image", "mp4", "webm", "anime_link"):
        op.execute(_STRIP_SQL.format(col=col))


def downgrade() -> None:
    # Stripping is irreversible — we don't know the original host.
    pass
