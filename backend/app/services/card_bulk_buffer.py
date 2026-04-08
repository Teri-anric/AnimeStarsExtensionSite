import json
import logging
import secrets
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Iterable
from uuid import UUID

from redis.exceptions import RedisError

from app.config import settings
from app.database.enum import CardType
from app.redis_client import get_redis

logger = logging.getLogger(__name__)

_UPSERT_REQUIRED_FIELDS = ("name", "rank")


@dataclass
class FlushResult:
    candidate_count: int
    written_count: int


class CardBulkBufferService:
    def __init__(self) -> None:
        prefix = settings.card_bulk.key_prefix
        self._dirty_set_key = f"{prefix}:dirty_ids"
        self._payload_key_prefix = f"{prefix}:payload"
        self._flush_lock_key = f"{prefix}:flush_lock"
        self._flush_lock_token: str | None = None

    def _payload_key(self, card_id: int) -> str:
        return f"{self._payload_key_prefix}:{card_id}"

    async def enqueue_cards(self, cards: Iterable[dict]) -> int:
        redis = get_redis()
        buffered = 0
        pipe = redis.pipeline(transaction=False)

        for card in cards:
            card_id = card.get("card_id")
            if card_id is None:
                continue
            card_id = int(card_id)

            mapping: dict[str, str] = {}
            for key, value in card.items():
                if key == "card_id" or value is None:
                    continue
                mapping[key] = json.dumps(self._to_json_compatible(value))

            if not mapping:
                continue

            pipe.hset(self._payload_key(card_id), mapping=mapping)
            pipe.sadd(self._dirty_set_key, card_id)
            buffered += 1

        if buffered:
            await pipe.execute()
        return buffered

    async def flush_into_repo(self, repo) -> FlushResult:
        if not await self._acquire_lock():
            return FlushResult(candidate_count=0, written_count=0)
        try:
            redis = get_redis()
            raw_ids = await redis.spop(
                self._dirty_set_key,
                settings.card_bulk.flush_batch_size,
            )
            if not raw_ids:
                return FlushResult(candidate_count=0, written_count=0)

            card_ids = [int(v) for v in raw_ids]
            payloads = await self._read_payloads(card_ids)
            if not payloads:
                return FlushResult(candidate_count=len(card_ids), written_count=0)

            full_upsert_values: list[dict] = []
            partial_update_values: list[dict] = []
            for payload in payloads:
                if all(field in payload for field in _UPSERT_REQUIRED_FIELDS):
                    full_upsert_values.append(payload)
                else:
                    partial_update_values.append(payload)

            total = 0
            if full_upsert_values:
                total += await repo.upsert_bulk(full_upsert_values)
            if partial_update_values:
                total += await repo.partial_update_by_card_id_bulk(partial_update_values)

            await redis.delete(*(self._payload_key(card_id) for card_id in card_ids))
            return FlushResult(candidate_count=len(card_ids), written_count=total)
        except Exception:
            # Requeue on failure to avoid data loss.
            await self._requeue_ids_from_error()
            raise
        finally:
            await self._release_lock()

    async def _read_payloads(self, card_ids: list[int]) -> list[dict]:
        redis = get_redis()
        pipe = redis.pipeline(transaction=False)
        for card_id in card_ids:
            pipe.hgetall(self._payload_key(card_id))
        raw_payloads = await pipe.execute()

        payloads: list[dict] = []
        for card_id, raw in zip(card_ids, raw_payloads):
            if not raw:
                continue
            payload = {"card_id": card_id}
            for key, value in raw.items():
                decoded_value = json.loads(value)
                if key == "rank" and isinstance(decoded_value, str):
                    try:
                        decoded_value = CardType(decoded_value)
                    except ValueError:
                        pass
                payload[key] = decoded_value
            payloads.append(payload)
        return payloads

    async def _acquire_lock(self) -> bool:
        redis = get_redis()
        token = secrets.token_hex(12)
        acquired = await redis.set(
            self._flush_lock_key,
            token,
            nx=True,
            ex=settings.card_bulk.lock_ttl_seconds,
        )
        if acquired:
            self._flush_lock_token = token
            return True
        return False

    async def _release_lock(self) -> None:
        if self._flush_lock_token is None:
            return
        redis = get_redis()
        lock_value = await redis.get(self._flush_lock_key)
        if lock_value == self._flush_lock_token:
            await redis.delete(self._flush_lock_key)
        self._flush_lock_token = None

    async def _requeue_ids_from_error(self) -> None:
        # If something failed after sPOP and before payload cleanup, keys still hold data.
        # Re-scan keys by pattern and rebuild dirty set as a best-effort recovery.
        redis = get_redis()
        cursor = "0"
        pattern = f"{self._payload_key_prefix}:*"
        ids_to_restore: list[int] = []

        while True:
            cursor, keys = await redis.scan(cursor=cursor, match=pattern, count=1000)
            for key in keys:
                try:
                    ids_to_restore.append(int(key.rsplit(":", 1)[-1]))
                except ValueError:
                    continue
            if cursor == "0":
                break

        if ids_to_restore:
            await redis.sadd(self._dirty_set_key, *ids_to_restore)

    @staticmethod
    def is_redis_error(exc: Exception) -> bool:
        return isinstance(exc, RedisError)

    @staticmethod
    def _to_json_compatible(value):
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, UUID):
            return str(value)
        return value
