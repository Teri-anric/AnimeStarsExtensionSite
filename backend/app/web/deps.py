from fastapi import Depends
from typing import Annotated

from app.database.repos.card import CardRepository
from app.database.repos.card_users_stats import CardUsersStatsRepository
from app.database.repos.animestars_user import AnimestarsUserRepo
from app.database.repos.deck import DeckRepository

CardRepositoryDep = Annotated[CardRepository, Depends(lambda: CardRepository())]
CardUsersStatsRepositoryDep = Annotated[
    CardUsersStatsRepository, Depends(lambda: CardUsersStatsRepository())
]
AnimestarsUserRepoDep = Annotated[AnimestarsUserRepo, Depends(lambda: AnimestarsUserRepo())]
DeckRepositoryDep = Annotated[DeckRepository, Depends(lambda: DeckRepository())]