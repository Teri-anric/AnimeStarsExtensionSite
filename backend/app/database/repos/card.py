from .animestars_user import AnimestarsUserRepo
from .crud import CRUDRepository
from .deck import DeckRepository
from .pagination import PaginationRepository
from app.config import settings
from ..enum import CardType
from ..models.animestars.card import Card
from ..models.animestars.card_users_stats import CardUsersStats
from .base import BaseRepository
from uuid import UUID
from typing import Iterable
from collections import defaultdict
from sqlalchemy import case, func, literal, or_, select, text, update, delete
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
        async with self.auto_commit() as session:
            return await self._upsert_bulk_in_session(session, cards)

    async def _upsert_bulk_in_session(self, session, cards: Iterable[dict]) -> int:
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
        await DeckRepository.attach_deck_ids(session, values)
        await AnimestarsUserRepo.ensure_authors_for_card_payloads(session, values)
        stmt = insert(Card).values(values)
        update_fields = (
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
            # Deck sync submits a complete snapshot repeatedly. Avoid rewriting
            # unchanged cards and creating needless row versions.
            where=or_(
                *(getattr(Card, field).is_distinct_from(getattr(stmt.excluded, field))
                  for field in update_fields)
            ),
        )
        result = await session.execute(stmt)
        return result.rowcount

    async def partial_update_by_card_id_bulk(self, cards: Iterable[dict]) -> int:
        """
        Partially update existing cards by card_id.

        Only fields provided in each payload will be updated; other fields remain unchanged.
        Cards are not created if they do not already exist.
        """
        all_cards = [
            {k: v for k, v in d.items()}
            for d in cards
            if d.get("card_id") is not None and len(d) > 1
        ]
        if not all_cards:
            return 0

        async with self.auto_commit() as session:
            return await self._partial_update_by_card_id_bulk_in_session(session, all_cards)

    async def _partial_update_by_card_id_bulk_in_session(self, session, all_cards: list[dict]) -> int:
        _updatable = {
            "name", "rank", "anime_name", "anime_link", "deck_id", "author", "image", "mp4", "webm",
        }
        if not all_cards:
            return 0
        need_deck = [d for d in all_cards if "anime_link" in d or "anime_name" in d]
        if need_deck:
            ids = [d["card_id"] for d in need_deck]
            existing_by_id = {
                c.card_id: c
                for c in (await session.scalars(select(Card).where(Card.card_id.in_(ids)))).all()
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
        need_author = [d for d in all_cards if "author" in d]
        if need_author:
            await AnimestarsUserRepo.ensure_authors_for_card_payloads(session, need_author)
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
                set_clause[field] = (
                    case(*whens, else_=Card.deck_id) if field == "deck_id" else case(*whens)
                )
            result = await session.execute(
                update(Card).where(Card.card_id.in_(card_ids)).values(**set_clause)
            )
            total += result.rowcount
        return total

    async def get_card_ids_by_deck_anime_id(self, anime_id: int) -> set[int]:
        from ..models.animestars.deck import AnimestarsDeck

        async with self.session as session:
            rows = await session.scalars(
                select(Card.card_id)
                .join(AnimestarsDeck, Card.deck_id == AnimestarsDeck.id)
                .where(AnimestarsDeck.anime_id == anime_id)
            )
            return set(rows.all())

    async def apply_bulk_changes(
        self,
        full_upserts: list[dict],
        partial_updates: list[dict],
        deleted: list[dict],
    ) -> int:
        """Apply every queued card operation in one database transaction."""
        async with self.auto_commit() as session:
            await session.execute(
                text(
                    "SET LOCAL lock_timeout = "
                    f"'{settings.card_bulk.database_lock_timeout_seconds}s'"
                )
            )
            total = 0
            delete_ids = [row["card_id"] for row in deleted if row.get("card_id")]
            if delete_ids:
                await session.execute(delete(CardUsersStats).where(CardUsersStats.card_id.in_(delete_ids)))
                result = await session.execute(delete(Card).where(Card.card_id.in_(delete_ids)))
                total += result.rowcount
            total = await self._upsert_bulk_in_session(session, full_upserts)
            total += await self._partial_update_by_card_id_bulk_in_session(session, partial_updates)
            return total

    async def get_card_ids_by_image_paths(self, paths: list[str]) -> dict[str, int]:
        """Map normalized image path → card_id (smallest card_id if duplicates)."""
        paths = [p for p in paths if p]
        if not paths:
            return {}
        stmt = select(Card.image, Card.card_id).where(Card.image.in_(paths))
        async with self.session as session:
            result = await session.execute(stmt)
            rows = result.all()
        return {row[0]: row[1] for row in rows}

    async def deck_rank_counts_by_reference_card_ids(
        self, card_ids: list[int]
    ) -> dict[int, dict[str, int]]:
        """
        For each reference card_id, count cards per rank in that card's deck.
        Missing card_id or null deck_id → all ranks zero.
        """
        unique_ids = sorted(set(card_ids))
        zeros = {t.value: 0 for t in CardType}
        if not unique_ids:
            return {}

        ref = (  # find all cards with a deck_id
            select(Card.card_id, Card.deck_id)
            .where(Card.card_id.in_(unique_ids), Card.deck_id.isnot(None))
            .cte("ref")
        )
        deck_counts = (  # count cards per rank in each deck
            select(Card.deck_id, Card.rank, func.count().label("cnt"))
            .where(Card.deck_id.in_(select(ref.c.deck_id).distinct()))
            .group_by(Card.deck_id, Card.rank)
            .cte("deck_counts")
        )
        stmt = select(ref.c.card_id, deck_counts.c.rank, deck_counts.c.cnt).select_from(
            ref.join(deck_counts, deck_counts.c.deck_id == ref.c.deck_id)
        )
        async with self.session as session:
            result = await session.execute(stmt)
            rows = result.all()
        out: dict[int, dict[str, int]] = {cid: dict(zeros) for cid in unique_ids}
        for card_id, rank, cnt in rows:
            if card_id not in out:
                continue
            key = rank.value if isinstance(rank, CardType) else str(rank)
            out[card_id][key] = int(cnt)
        return out
