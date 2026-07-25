from fastapi import Depends
from typing import Annotated

from app.database.repos.card import CardRepository
from app.database.repos.card_users_stats import CardUsersStatsRepository
from app.database.repos.animestars_user import AnimestarsUserRepo
from app.database.repos.deck import DeckRepository
from app.database.repos.extension_banner import ExtensionBannerRepository
from app.database.repos.extension_labyrinth_room import ExtensionLabyrinthRoomRepository
from app.database.repos.health import HealthRepository
from app.parser.services import VerificationService
from app.services import CardBulkBufferService, CardStatsCacheService
from app.services.extension_card_image_cache import ExtensionCardImageCacheService

CardRepositoryDep = Annotated[CardRepository, Depends(lambda: CardRepository())]
CardUsersStatsRepositoryDep = Annotated[
    CardUsersStatsRepository, Depends(lambda: CardUsersStatsRepository())
]
AnimestarsUserRepoDep = Annotated[AnimestarsUserRepo, Depends(lambda: AnimestarsUserRepo())]
DeckRepositoryDep = Annotated[DeckRepository, Depends(lambda: DeckRepository())]
HealthRepositoryDep = Annotated[HealthRepository, Depends(lambda: HealthRepository())]
ExtensionBannerRepositoryDep = Annotated[
    ExtensionBannerRepository, Depends(lambda: ExtensionBannerRepository())
]
ExtensionLabyrinthRoomRepositoryDep = Annotated[
    ExtensionLabyrinthRoomRepository, Depends(lambda: ExtensionLabyrinthRoomRepository())
]

VerificationServiceDep = Annotated[VerificationService, Depends(lambda: VerificationService())]
CardBulkBufferServiceDep = Annotated[
    CardBulkBufferService, Depends(lambda: CardBulkBufferService())
]
CardStatsCacheServiceDep = Annotated[
    CardStatsCacheService, Depends(lambda: CardStatsCacheService())
]
ExtensionCardImageCacheServiceDep = Annotated[
    ExtensionCardImageCacheService, Depends(lambda: ExtensionCardImageCacheService())
]
