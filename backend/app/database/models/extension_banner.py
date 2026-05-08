from sqlalchemy import Boolean, Column, String

from .base import Base, TimestampMixin, UUIDPKMixin


class ExtensionBanner(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "extension_banners"

    title = Column(String(120), nullable=False, default="AnimeStars Extension")
    message = Column(
        String(500),
        nullable=False,
        default="Latest extension update is available now.",
    )
    action_text = Column(String(80), nullable=True)
    action_url = Column(String(512), nullable=True)
    is_active = Column(Boolean, nullable=False, default=False)
