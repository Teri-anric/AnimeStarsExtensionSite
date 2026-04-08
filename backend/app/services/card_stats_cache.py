import json
from datetime import datetime
from uuid import uuid4
from uuid import UUID

from app.config import settings
from app.database.enum import CardCollection
from app.database.models.animestars.card_users_stats import CardUsersStats
from app.redis_client import get_redis


class CardStatsCacheService:
    def __init__(self) -> None:
        self._key_prefix = settings.card_stats_cache.key_prefix
        self._ttl_seconds = settings.card_stats_cache.ttl_seconds

    def _key(self, card_id: int) -> str:
        return f"{self._key_prefix}:{card_id}"

    async def get_last_bulk(self, repo, card_ids: list[int]) -> list[CardUsersStats]:
        if not card_ids:
            return []

        unique_card_ids = sorted(set(card_ids))
        cache_by_card_id: dict[int, list[CardUsersStats]] = {}
        missed_card_ids: list[int] = []

        redis = get_redis()
        try:
            pipe = redis.pipeline(transaction=False)
            for card_id in unique_card_ids:
                pipe.get(self._key(card_id))
            cached_values = await pipe.execute()

            for card_id, raw_cached in zip(unique_card_ids, cached_values):
                if raw_cached:
                    cache_by_card_id[card_id] = self._deserialize_stats(raw_cached)
                else:
                    missed_card_ids.append(card_id)
        except Exception:
            missed_card_ids = unique_card_ids

        fetched_by_card_id: dict[int, list[CardUsersStats]] = {}
        if missed_card_ids:
            fetched = await repo.get_last_card_users_stats_bulk(missed_card_ids)
            fetched_by_card_id = self._group_by_card_id(fetched)
            await self._cache_many_best_effort(fetched_by_card_id, missed_card_ids)

        merged_by_card_id = {**cache_by_card_id, **fetched_by_card_id}
        merged_results: list[CardUsersStats] = []
        for card_id in unique_card_ids:
            merged_results.extend(merged_by_card_id.get(card_id, []))
        return merged_results

    async def refresh_after_add(self, events: list[dict]) -> None:
        if not events:
            return

        events_by_card: dict[int, list[dict]] = {}
        for event in events:
            card_id = event.get("card_id")
            if card_id is None:
                continue
            events_by_card.setdefault(int(card_id), []).append(event)
        if not events_by_card:
            return

        unique_card_ids = sorted(events_by_card.keys())
        redis = get_redis()
        pipe = redis.pipeline(transaction=False)
        for card_id in unique_card_ids:
            pipe.get(self._key(card_id))
        cached_values = await pipe.execute()

        updated_payloads: dict[int, str] = {}
        for card_id, raw_cached in zip(unique_card_ids, cached_values):
            # If cache key does not exist, skip write to avoid partial cache snapshots.
            if not raw_cached:
                continue

            current_items = self._deserialize_stats(raw_cached)
            by_collection: dict[CardCollection, CardUsersStats] = {
                item.collection: item for item in current_items
            }
            changed = False

            for event in events_by_card.get(card_id, []):
                collection = self._as_collection(event.get("collection"))
                if collection is None:
                    continue
                created_at = event.get("created_at")
                count = event.get("count")
                if not isinstance(created_at, datetime) or not isinstance(count, int):
                    continue

                existing = by_collection.get(collection)
                if existing is None or created_at >= existing.created_at:
                    if existing is None:
                        by_collection[collection] = CardUsersStats(
                            id=uuid4(),
                            owner_id=None,
                            card_id=card_id,
                            collection=collection,
                            count=count,
                            created_at=created_at,
                            updated_at=created_at,
                        )
                    else:
                        existing.count = count
                        existing.created_at = created_at
                        existing.updated_at = created_at
                    changed = True

            if changed:
                updated_payloads[card_id] = self._serialize_stats(list(by_collection.values()))

        if not updated_payloads:
            return

        pipe = redis.pipeline(transaction=False)
        for card_id, payload in updated_payloads.items():
            if self._ttl_seconds > 0:
                pipe.set(self._key(card_id), payload, ex=self._ttl_seconds)
            else:
                pipe.set(self._key(card_id), payload)
        await pipe.execute()

    async def _cache_many_best_effort(
        self,
        grouped: dict[int, list[CardUsersStats]],
        card_ids: list[int],
    ) -> None:
        redis = get_redis()
        try:
            pipe = redis.pipeline(transaction=False)
            for card_id in card_ids:
                payload = self._serialize_stats(grouped.get(card_id, []))
                if self._ttl_seconds > 0:
                    pipe.set(self._key(card_id), payload, ex=self._ttl_seconds)
                else:
                    pipe.set(self._key(card_id), payload)
            await pipe.execute()
        except Exception:
            pass

    @staticmethod
    def _serialize_stats(results: list[CardUsersStats]) -> str:
        return json.dumps(
            [
                {
                    "id": str(item.id),
                    "owner_id": str(item.owner_id) if item.owner_id else None,
                    "card_id": item.card_id,
                    "collection": item.collection.value,
                    "count": item.count,
                    "created_at": item.created_at.isoformat(),
                    "updated_at": item.updated_at.isoformat(),
                }
                for item in results
            ]
        )

    @staticmethod
    def _deserialize_stats(raw: str) -> list[CardUsersStats]:
        payload = json.loads(raw)
        restored: list[CardUsersStats] = []
        for item in payload:
            restored.append(
                CardUsersStats(
                    id=UUID(item["id"]),
                    owner_id=UUID(item["owner_id"]) if item["owner_id"] else None,
                    card_id=item["card_id"],
                    collection=CardCollection(item["collection"]),
                    count=item["count"],
                    created_at=datetime.fromisoformat(item["created_at"]),
                    updated_at=datetime.fromisoformat(item["updated_at"]),
                )
            )
        return restored

    @staticmethod
    def _group_by_card_id(results: list[CardUsersStats]) -> dict[int, list[CardUsersStats]]:
        grouped: dict[int, list[CardUsersStats]] = {}
        for row in results:
            grouped.setdefault(row.card_id, []).append(row)
        return grouped

    @staticmethod
    def _as_collection(value) -> CardCollection | None:
        if isinstance(value, CardCollection):
            return value
        if isinstance(value, str):
            try:
                return CardCollection(value)
            except ValueError:
                return None
        return None
