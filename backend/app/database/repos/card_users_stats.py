from uuid import UUID
from sqlalchemy import select, text, bindparam, Integer, case, update
from ..models.animestars.card_users_stats import CardUsersStats
from ..models.animestars.card import Card
from ..enum import CardCollection
from .base import BaseRepository
from .crud import CRUDRepository
from .pagination import PaginationRepository


class CardUsersStatsRepository(
    CRUDRepository[CardUsersStats, UUID],
    PaginationRepository[CardUsersStats],
    BaseRepository,
):
    @property
    def entry_class(self) -> type[CardUsersStats]:
        return CardUsersStats

    @property
    def entry_code(self) -> str:
        return "card_users_stats"

    async def add_stats_and_update_current(self, events: list[dict]) -> None:
        """Append the batch and atomically advance each card's current snapshot."""
        if not events:
            return
        latest: dict[tuple[int, CardCollection], dict] = {}
        for event in events:
            key = (event["card_id"], event["collection"])
            previous = latest.get(key)
            if previous is None or event["created_at"] >= previous["created_at"]:
                latest[key] = event
        normalized = list(latest.values())
        card_ids = sorted({event["card_id"] for event in normalized})

        async with self.auto_commit() as session:
            cards = list(
                (
                    await session.scalars(
                        select(Card)
                        .where(Card.card_id.in_(card_ids))
                        .order_by(Card.card_id)
                        .with_for_update()
                    )
                ).all()
            )
            found = {card.card_id for card in cards}
            missing = sorted(set(card_ids) - found)
            if missing:
                raise ValueError(f"Unknown card_id(s): {missing}")

            session.add_all(
                CardUsersStats(owner_id=None, **event) for event in normalized
            )

            values = {}
            for collection, count_field, timestamp_field in (
                (CardCollection.TRADE, Card.trade_count, Card.trade_updated_at),
                (CardCollection.NEED, Card.need_count, Card.need_updated_at),
                (CardCollection.OWNED, Card.owned_count, Card.owned_updated_at),
                (
                    CardCollection.UNLOCKED_OWNED,
                    Card.unlocked_owned_count,
                    Card.unlocked_owned_updated_at,
                ),
            ):
                collection_events = {
                    event["card_id"]: event
                    for event in normalized
                    if event["collection"] == collection
                }
                if not collection_events:
                    continue
                values[count_field] = case(
                    *(
                        (
                            Card.card_id == card_id,
                            case(
                                (timestamp_field.is_(None), event["count"]),
                                (
                                    timestamp_field <= event["created_at"],
                                    event["count"],
                                ),
                                else_=count_field,
                            ),
                        )
                        for card_id, event in collection_events.items()
                    ),
                    else_=count_field,
                )
                values[timestamp_field] = case(
                    *(
                        (
                            Card.card_id == card_id,
                            case(
                                (timestamp_field.is_(None), event["created_at"]),
                                (
                                    timestamp_field <= event["created_at"],
                                    event["created_at"],
                                ),
                                else_=timestamp_field,
                            ),
                        )
                        for card_id, event in collection_events.items()
                    ),
                    else_=timestamp_field,
                )
            await session.execute(
                update(Card).where(Card.card_id.in_(card_ids)).values(values)
            )

    async def aggregate_stats_per_second(self, older_than_days: int = 7) -> int:
        """
        Aggregate duplicate stats so that, for rows older than N days, there is
        at most one record per (owner_id, card_id, collection, second).

        Only duplicate groups are touched. The former DELETE + INSERT rewrote
        every old row, competed with the card flush for locks, and raw SQL did
        not have an ORM-generated UUID for the replacement row.
        """
        sql = text("""
            WITH ranked AS (
                SELECT
                    id,
                    owner_id,
                    card_id,
                    collection,
                    date_trunc('second', created_at) AS created_at_sec,
                    ROUND(AVG(count) OVER (
                        PARTITION BY owner_id, card_id, collection, date_trunc('second', created_at)
                    ))::integer AS avg_count,
                    COUNT(*) OVER (
                        PARTITION BY owner_id, card_id, collection, date_trunc('second', created_at)
                    ) AS group_count,
                    ROW_NUMBER() OVER (
                        PARTITION BY owner_id, card_id, collection, date_trunc('second', created_at)
                        ORDER BY created_at, id
                    ) AS row_number
                FROM animestars_card_users_stats
                WHERE created_at < now() - make_interval(days => :days)
            ),
            updated AS (
                UPDATE animestars_card_users_stats AS stats
                SET count = ranked.avg_count,
                    created_at = ranked.created_at_sec
                FROM ranked
                WHERE stats.id = ranked.id
                  AND ranked.row_number = 1
                  AND ranked.group_count > 1
                RETURNING stats.id
            ),
            deleted AS (
                DELETE FROM animestars_card_users_stats AS stats
                USING ranked
                WHERE stats.id = ranked.id
                  AND ranked.row_number > 1
                RETURNING stats.id
            )
            SELECT
                (SELECT count(*) FROM updated) + (SELECT count(*) FROM deleted) AS affected;
            """).bindparams(bindparam("days", type_=Integer))

        async with self.auto_commit() as session:
            result = await session.execute(sql, {"days": older_than_days})
            return int(result.scalar_one())
