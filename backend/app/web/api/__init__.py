from fastapi import APIRouter

from .card import router as card_router
from .auth import router as auth_router
from .deck import router as deck_router
from .card_stats import router as card_stats_router
from .extension import router as extension_router
from .files import router as files_router


__all__ = ["card_router", "auth_router", "deck_router", "card_stats_router", "extension_router", "files_router"]


router = APIRouter(prefix="/api")

router.include_router(card_router)
router.include_router(auth_router)
router.include_router(deck_router)
router.include_router(card_stats_router)
router.include_router(extension_router)
router.include_router(files_router)