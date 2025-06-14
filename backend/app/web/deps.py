from fastapi import Depends
from typing import Annotated

from app.database.repos.card import CardRepository
from app.database.repos.summary_card_users import SummaryCardUsersRepository
from app.database.repos.animestars_user import AnimestarsUserRepo
from app.database.repos.deck import DeckRepository

CardRepositoryDep = Annotated[CardRepository, Depends(lambda: CardRepository())]
SummaryCardUsersRepositoryDep = Annotated[
    SummaryCardUsersRepository, Depends(lambda: SummaryCardUsersRepository())
]
AnimestarsUserRepoDep = Annotated[AnimestarsUserRepo, Depends(lambda: AnimestarsUserRepo())]
DeckRepositoryDep = Annotated[DeckRepository, Depends(lambda: DeckRepository())]