import asyncio

from app.config import settings
from app.json_logging import configure_json_app_logging

configure_json_app_logging(settings.log_json)

from .scheduler import scheduler
from .tasks import update_cards  # noqa: F401


async def idle(scheduler):
    while scheduler.running:
        await asyncio.sleep(60 * 60)


async def main():
    from app.redis_client import close_redis

    scheduler.start()
    try:
        await idle(scheduler)
    finally:
        await close_redis()


if __name__ == "__main__":
    asyncio.run(main())
