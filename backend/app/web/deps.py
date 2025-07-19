from fastapi import Depends
from typing import Annotated

from app.database.repos.card import CardRepository
from app.database.repos.card_users_stats import CardUsersStatsRepository
from app.database.repos.animestars_user import AnimestarsUserRepo
from app.database.repos.deck import DeckRepository
from app.database.repos.health import HealthRepository
from app.parser.services import VerificationService
from app.storage import LocalStorageService

CardRepositoryDep = Annotated[CardRepository, Depends(lambda: CardRepository())]
CardUsersStatsRepositoryDep = Annotated[
    CardUsersStatsRepository, Depends(lambda: CardUsersStatsRepository())
]
AnimestarsUserRepoDep = Annotated[AnimestarsUserRepo, Depends(lambda: AnimestarsUserRepo())]
DeckRepositoryDep = Annotated[DeckRepository, Depends(lambda: DeckRepository())]
HealthRepositoryDep = Annotated[HealthRepository, Depends(lambda: HealthRepository())]

VerificationServiceDep = Annotated[VerificationService, Depends(lambda: VerificationService())]

# Storage service dependency
def get_storage_service() -> LocalStorageService:
    return LocalStorageService()

StorageServiceDep = Annotated[LocalStorageService, Depends(get_storage_service)]