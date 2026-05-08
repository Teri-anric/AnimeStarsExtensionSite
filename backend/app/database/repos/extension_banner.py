from sqlalchemy import select

from app.database.models.extension_banner import ExtensionBanner

from .base import BaseRepository


class ExtensionBannerRepository(BaseRepository):
    async def get_or_create(self) -> ExtensionBanner:
        banner = await self.scalar(select(ExtensionBanner).limit(1))
        if banner is not None:
            return banner

        return await self.add(ExtensionBanner())

    async def update_banner(
        self,
        *,
        title: str,
        message: str,
        action_text: str | None,
        action_url: str | None,
        is_active: bool,
    ) -> ExtensionBanner:
        async with self.session as session:
            result = await session.execute(select(ExtensionBanner).limit(1))
            banner = result.scalar_one_or_none()
            if banner is None:
                banner = ExtensionBanner()
                session.add(banner)

            banner.title = title
            banner.message = message
            banner.action_text = action_text
            banner.action_url = action_url
            banner.is_active = is_active

            await session.commit()
            await session.refresh(banner)
            return banner
