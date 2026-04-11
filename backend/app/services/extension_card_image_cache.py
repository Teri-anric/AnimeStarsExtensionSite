import json
import logging

from app.config import settings
from app.database.repos.card import CardRepository
from app.redis_client import get_redis
from app.web.util.media_path import normalize_media_path

logger = logging.getLogger(__name__)


class ExtensionCardImageCacheService:
    """Redis cache for image path → card_id (extension batch resolver)."""

    def __init__(self) -> None:
        self._key_prefix = "extension:card_image"
        self._ttl_seconds = settings.card_stats_cache.ttl_seconds

    def _key(self, normalized_path: str) -> str:
        return f"{self._key_prefix}:{normalized_path}"

    async def resolve_images(
        self,
        repo: CardRepository,
        raw_images: list[str],
    ) -> list[tuple[str, int | None]]:
        """
        Preserve input order. Each tuple is (normalized_path, card_id or None).
        Positive hits are cached; misses are not cached.
        """
        if not raw_images:
            return []

        norm_in_order = [normalize_media_path(p) for p in raw_images]
        unique_nonempty: list[str] = []
        seen: set[str] = set()
        for n in norm_in_order:
            if n and n not in seen:
                seen.add(n)
                unique_nonempty.append(n)

        cached: dict[str, int] = {}
        missed: list[str] = list(unique_nonempty)

        if unique_nonempty:
            redis = get_redis()
            try:
                pipe = redis.pipeline(transaction=False)
                for path in unique_nonempty:
                    pipe.get(self._key(path))
                raw_values = await pipe.execute()
                still_missed: list[str] = []
                for path, raw in zip(unique_nonempty, raw_values):
                    if not raw:
                        still_missed.append(path)
                        continue
                    try:
                        cid = json.loads(raw).get("card_id")
                        if isinstance(cid, int):
                            cached[path] = cid
                        else:
                            still_missed.append(path)
                    except (json.JSONDecodeError, TypeError):
                        still_missed.append(path)
                missed = still_missed
            except Exception:
                logger.exception("extension card image cache read failed")
                missed = list(unique_nonempty)

        db_map: dict[str, int] = {}
        if missed:
            db_map = await repo.get_card_ids_by_image_paths(missed)
            await self._cache_positive_best_effort(db_map)

        combined = {**cached, **db_map}
        return [(n, combined.get(n) if n else None) for n in norm_in_order]

    async def _cache_positive_best_effort(self, path_to_id: dict[str, int]) -> None:
        if not path_to_id:
            return
        redis = get_redis()
        try:
            pipe = redis.pipeline(transaction=False)
            for path, card_id in path_to_id.items():
                payload = json.dumps({"card_id": card_id})
                if self._ttl_seconds > 0:
                    pipe.set(self._key(path), payload, ex=self._ttl_seconds)
                else:
                    pipe.set(self._key(path), payload)
            await pipe.execute()
        except Exception:
            logger.exception("extension card image cache write failed")
