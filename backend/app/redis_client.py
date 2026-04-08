from redis.asyncio import Redis

from app.config import settings

_redis_client: Redis | None = None


def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db,
            username=settings.redis.username,
            password=settings.redis.password,
            ssl=settings.redis.ssl,
            socket_timeout=settings.redis.socket_timeout_seconds,
            decode_responses=True,
        )
    return _redis_client


async def close_redis() -> None:
    global _redis_client
    if _redis_client is None:
        return
    await _redis_client.aclose()
    _redis_client = None
