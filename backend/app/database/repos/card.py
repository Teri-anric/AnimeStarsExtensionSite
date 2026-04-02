from .animestars_user import AnimestarsUserRepo
from .crud import CRUDRepository
from .deck import DeckRepository
from .pagination import PaginationRepository
from ..models.animestars.card import Card
from ..models.animestars.card_users_stats import CardUsersStats
from .base import BaseRepository
from uuid import UUID
from typing import Iterable
from collections import defaultdict
from sqlalchemy import case, literal, select, update, delete
from sqlalchemy.dialects.postgresql import insert


class CardRepository(
    CRUDRepository[Card, UUID], PaginationRepository[Card], BaseRepository
):
    @property
    def entry_class(self) -> type[Card]:
        return Card

    async def create(self, **kwargs) -> Card:
        async with self.session as session:
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
        insert_fields = (
            "card_id",
            "name",
            "rank",
            "anime_name",
            "anime_link",
            "deck_id",
            "author",
            "image",
            "mp4",
            "webm",
        )
        values = [{field: row.get(field) for field in insert_fields} for row in values]
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
        _updatable = {"name", "rank", "anime_name", "anime_link", "deck_id", "author", "image", "mp4", "webm"}

        all_cards = [
            {k: v for k, v in d.items()}
            for d in cards
            if d.get("card_id") is not None and len(d) > 1
        ]
        if not all_cards:
            return 0

        async with self.auto_commit() as session:
            # Batch deck resolution: one SELECT + one INSERT instead of N of each
            need_deck = [d for d in all_cards if "anime_link" in d or "anime_name" in d]
            if need_deck:
                ids = [d["card_id"] for d in need_deck]
                existing_by_id = {
                    c.card_id: c
                    for c in (
                        await session.scalars(select(Card).where(Card.card_id.in_(ids)))
                    ).all()
                }
                for d in need_deck:
                    ex = existing_by_id.get(d["card_id"])
                    if ex:
                        d.setdefault("anime_link", ex.anime_link)
                        d.setdefault("anime_name", ex.anime_name)
                await DeckRepository.attach_deck_ids(session, need_deck)
                deck_by_card_id = {d["card_id"]: d.get("deck_id") for d in need_deck}
                for d in all_cards:
                    if d["card_id"] in deck_by_card_id:
                        d["deck_id"] = deck_by_card_id[d["card_id"]]

            # Batch author resolution: one call instead of N
            need_author = [d for d in all_cards if "author" in d]
            if need_author:
                await AnimestarsUserRepo.ensure_authors_for_card_payloads(session, need_author)

            # Batch UPDATE: group by field set → one UPDATE per group via CASE WHEN
            groups: dict[frozenset, list[dict]] = defaultdict(list)
            for d in all_cards:
                key = frozenset(k for k in d if k != "card_id" and k in _updatable)
                if key:
                    groups[key].append(d)

            total = 0
            for fields_set, group in groups.items():
                card_ids = [d["card_id"] for d in group]
                val_by_id = {d["card_id"]: d for d in group}
                set_clause = {}
                for field in fields_set:
                    whens = []
                    for cid in card_ids:
                        value = val_by_id[cid][field]
                        if field == "deck_id":
                            value = literal(value, type_=Card.deck_id.type)
                        whens.append((Card.card_id == cid, value))
                    expr = (
                        case(*whens, else_=Card.deck_id)
                        if field == "deck_id"
                        else case(*whens)
                    )
                    set_clause[field] = expr
                result = await session.execute(
                    update(Card).where(Card.card_id.in_(card_ids)).values(**set_clause)
                )
                total += result.rowcount

        return total
