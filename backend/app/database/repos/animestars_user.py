from sqlalchemy import select, func

from .base import BaseRepository
from .crud import CRUDRepository
from .pagination import PaginationRepository

from ..models.animestars.user import AnimestarsUser


class AnimestarsUserRepo(CRUDRepository, PaginationRepository, BaseRepository):
    @property
    def entry_class(self) -> type[AnimestarsUser]:
        return AnimestarsUser

    async def get_by_username(self, username: str) -> AnimestarsUser | None:
        return await self.scalar(select(AnimestarsUser).where(func.lower(AnimestarsUser.username) == username.lower()))