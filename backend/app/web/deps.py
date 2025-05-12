from fastapi import Depends
from typing import Annotated

from app.database.repos.card import CardRepository
from app.database.repos.summary_card_users import SummaryCardUsersRepository


CardRepositoryDep = Annotated[CardRepository, Depends(lambda: CardRepository())]
SummaryCardUsersRepositoryDep = Annotated[
    SummaryCardUsersRepository, Depends(lambda: SummaryCardUsersRepository())
]
