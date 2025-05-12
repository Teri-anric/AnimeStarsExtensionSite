import asyncio
from .scheduler import scheduler
from .tasks import update_cards # noqa


async def idle(scheduler):
    while scheduler.running:
        await asyncio.sleep(60 * 60)


async def main():
    scheduler.start()
    await idle(scheduler)


if __name__ == "__main__":
    asyncio.run(main())
