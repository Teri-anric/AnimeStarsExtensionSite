from .animestars_user import AnimestarsUserRepo
from .crud import CRUDRepository
from .deck import DeckRepository
from .pagination import PaginationRepository
from ..models.animestars.card import Card
from ..models.animestars.card_users_stats import CardUsersStats
from .base import BaseRepository
from uuid import UUID
from typing import Iterable
from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert


class CardRepository(
    CRUDRepository[Card, UUID], PaginationRepository[Card], BaseRepository
):
    @property
    def entry_class(self) -> type[Card]:
        return Card

    async def create(self, **kwargs) -> Card:
        async with self.auto_commit() as session:
            kwargs["deck_id"] = await DeckRepository.ensure_deck_id(
                session, kwargs.get("anime_link"), kwargs.get("anime_name")
            )
            obj = Card(**kwargs)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def update(self, id: UUID, **kwargs) -> int:
        if "anime_link" not in kwargs and "anime_name" not in kwargs:
            async with self.auto_commit() as session:
                result = await session.execute(
                    update(Card).where(Card.id.__eq__(id)).values(**kwargs)
                )
                return result.rowcount
        async with self.auto_commit() as session:
            card = await session.get(Card, id)
            if not card:
                return 0
            anime_link = (
                kwargs["anime_link"] if "anime_link" in kwargs else card.anime_link
            )
            anime_name = (
                kwargs["anime_name"] if "anime_name" in kwargs else card.anime_name
            )
            kwargs = {
                **kwargs,
                "deck_id": await DeckRepository.ensure_deck_id(
                    session, anime_link, anime_name
                ),
            }
            result = await session.execute(
                update(Card).where(Card.id.__eq__(id)).values(**kwargs)
            )
            return result.rowcount

    async def get_by_card_id(self, card_id: int) -> Card | None:
        return await self.scalar(select(Card).where(Card.card_id == card_id))

    async def get_by_ident(self, ident: int | UUID) -> Card | None:
        if isinstance(ident, int):
            return await self.get_by_card_id(ident)
        return await self.get(ident)

    async def delete_by_ident(self, ident: int | UUID) -> bool:
        """Remove card and related user stats (FK on card_id has no CASCADE)."""
        async with self.auto_commit() as session:
            if isinstance(ident, int):
                card = await session.scalar(select(Card).where(Card.card_id == ident))
            else:
                card = await session.scalar(select(Card).where(Card.id == ident))
            if not card:
                return False
            await session.execute(
                delete(CardUsersStats).where(CardUsersStats.card_id == card.card_id)
            )
            await session.execute(delete(Card).where(Card.id == card.id))
        return True

    async def upsert_bulk(self, cards: Iterable[dict]) -> int:
        values = list(cards)
        if not values:
            return 0
        async with self.auto_commit() as session:
            await DeckRepository.attach_deck_ids(session, values)
            await AnimestarsUserRepo.ensure_authors_for_card_payloads(session, values)
            stmt = insert(Card).values(values)
            stmt = stmt.on_conflict_do_update(
                index_elements=["card_id"],
                set_={
                    "name": stmt.excluded.name,
                    "rank": stmt.excluded.rank,
                    "anime_name": stmt.excluded.anime_name,
                    "anime_link": stmt.excluded.anime_link,
                    "deck_id": stmt.excluded.deck_id,
                    "author": stmt.excluded.author,
                    "image": stmt.excluded.image,
                    "mp4": stmt.excluded.mp4,
                    "webm": stmt.excluded.webm,
                },
            )
            result = await session.execute(stmt)
        return result.rowcount

    async def partial_update_by_card_id_bulk(self, cards: Iterable[dict]) -> int:
        """
        Partially update existing cards by card_id.

        Only fields provided in each payload will be updated; other fields remain unchanged.
        Cards are not created if they do not already exist.
        """
        total = 0
        async with self.auto_commit() as session:
            for data in cards:
                card_id = data.get("card_id")
                if card_id is None:
                    continue
                fields = {k: v for k, v in data.items() if k != "card_id"}
                if not fields:
                    continue
                if "anime_link" in fields or "anime_name" in fields:
                    existing = await session.scalar(
                        select(Card).where(Card.card_id == card_id)
                    )
                    if existing:
                        al = (
                            fields["anime_link"]
                            if "anime_link" in fields
                            else existing.anime_link
                        )
                        an = (
                            fields["anime_name"]
                            if "anime_name" in fields
                            else existing.anime_name
                        )
                        fields["deck_id"] = await DeckRepository.ensure_deck_id(
                            session, al, an
                        )
                    elif fields.get("anime_link"):
                        fields["deck_id"] = await DeckRepository.ensure_deck_id(
                            session,
                            fields.get("anime_link"),
                            fields.get("anime_name"),
                        )
                if "author" in fields:
                    await AnimestarsUserRepo.ensure_authors_for_card_payloads(
                        session, [fields]
                    )
                result = await session.execute(
                    update(Card).where(Card.card_id == card_id).values(**fields)
                )
                total += result.rowcount
        return total
