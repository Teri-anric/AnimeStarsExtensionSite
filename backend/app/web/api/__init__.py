from fastapi import APIRouter

from .card import router as card_router


__all__ = ["card_router"]


router = APIRouter(prefix="/api")

router.include_router(card_router)
