import uuid
from typing import Any, Iterable

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

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

    @staticmethod
    async def ensure_authors_for_card_payloads(
        session: AsyncSession, payloads: Iterable[dict[str, Any]]
    ) -> None:
        """
        Ensure each non-empty `author` in payloads references an existing `animestars_users` row
        (FK on Card.author -> AnimestarsUser.username). Creates missing users and normalizes
        casing to the stored username when a case-insensitive match exists.
        """
        payloads = list(payloads)
        needed_lowers: set[str] = set()
        first_casing: dict[str, str] = {}

        for d in payloads:
            if "author" not in d:
                continue
            a = d["author"]
            if a is None:
                continue
            s = str(a).strip()
            if not s:
                d["author"] = None
                continue
            lk = s.lower()
            needed_lowers.add(lk)
            first_casing.setdefault(lk, s)

        if not needed_lowers:
            return

        result = await session.execute(
            select(AnimestarsUser.username).where(
                func.lower(AnimestarsUser.username).in_(needed_lowers)
            )
        )
        exact_by_lower = {row[0].lower(): row[0] for row in result.all()}

        missing = [first_casing[lk] for lk in needed_lowers if lk not in exact_by_lower]
        if missing:
            rows = [
                {
                    "id": uuid.uuid4(),
                    "username": un,
                    "created_at": func.now(),
                    "updated_at": func.now(),
                }
                for un in missing
            ]
            stmt = pg_insert(AnimestarsUser).values(rows)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=[func.lower(AnimestarsUser.username)],
            )
            await session.execute(stmt)

            result = await session.execute(
                select(AnimestarsUser.username).where(
                    func.lower(AnimestarsUser.username).in_(needed_lowers)
                )
            )
            exact_by_lower = {row[0].lower(): row[0] for row in result.all()}

        for d in payloads:
            if "author" not in d:
                continue
            a = d.get("author")
            if a is None:
                continue
            s = str(a).strip()
            if not s:
                d["author"] = None
                continue
            lk = s.lower()
            d["author"] = exact_by_lower.get(lk, s)
