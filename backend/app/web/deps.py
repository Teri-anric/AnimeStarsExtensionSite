from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repos.card import CardRepository
from app.database.repos.card_users_stats import CardUsersStatsRepository
from app.database.repos.animestars_user import AnimestarsUserRepo
from app.database.repos.deck import DeckRepository
from app.database.repos.health import HealthRepository
from app.database.connection import get_async_session

CardRepositoryDep = Annotated[CardRepository, Depends(lambda: CardRepository())]
CardUsersStatsRepositoryDep = Annotated[
    CardUsersStatsRepository, Depends(lambda: CardUsersStatsRepository())
]
AnimestarsUserRepoDep = Annotated[AnimestarsUserRepo, Depends(lambda: AnimestarsUserRepo())]
DeckRepositoryDep = Annotated[DeckRepository, Depends(lambda: DeckRepository())]
HealthRepositoryDep = Annotated[HealthRepository, Depends(lambda: HealthRepository())]

async def get_db() -> AsyncSession:
    async with get_async_session() as session:
        yield session

DatabaseDep = Annotated[AsyncSession, Depends(get_db)]