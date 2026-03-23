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
    scheduler.start()
    await idle(scheduler)


if __name__ == "__main__":
    asyncio.run(main())
