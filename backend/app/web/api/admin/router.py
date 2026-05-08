from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.config import settings
from app.database.models.user import User
from app.web.auth.deps import UserDep
from app.web.deps import ExtensionBannerRepositoryDep, HealthRepositoryDep

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminDatabaseStatsResponse(BaseModel):
    total_cards: int
    total_users: int
    cards_with_stats: int
    cards_stats_today: int


class AdminExtensionBannerResponse(BaseModel):
    title: str
    message: str
    action_text: str | None = None
    action_url: str | None = None
    is_active: bool


class AdminExtensionBannerUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    message: str = Field(..., min_length=1, max_length=500)
    action_text: str | None = Field(default=None, max_length=80)
    action_url: str | None = Field(default=None, max_length=512)
    is_active: bool


async def require_admin_user(current_user: UserDep) -> User:
    if current_user.username != settings.admin_username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


AdminUserDep = Annotated[User, Depends(require_admin_user)]


@router.get("/database-stats", response_model=AdminDatabaseStatsResponse)
async def admin_database_stats(
    _admin_user: AdminUserDep,
    health_repo: HealthRepositoryDep,
):
    total_cards_count = await health_repo.get_total_cards_count()
    total_users_count = await health_repo.get_total_users_count()
    total_cards_with_stats_count = await health_repo.get_total_cards_with_stats_count()
    total_cards_stats_today_count = await health_repo.get_total_cards_stats_today_count()

    return {
        "total_cards": total_cards_count,
        "total_users": total_users_count,
        "cards_with_stats": total_cards_with_stats_count,
        "cards_stats_today": total_cards_stats_today_count,
    }


@router.get("/extension-banner", response_model=AdminExtensionBannerResponse)
async def get_extension_banner(
    _admin_user: AdminUserDep,
    banner_repo: ExtensionBannerRepositoryDep,
):
    banner = await banner_repo.get_or_create()
    return AdminExtensionBannerResponse(
        title=banner.title,
        message=banner.message,
        action_text=banner.action_text,
        action_url=banner.action_url,
        is_active=banner.is_active,
    )


@router.put("/extension-banner", response_model=AdminExtensionBannerResponse)
async def update_extension_banner(
    payload: AdminExtensionBannerUpdateRequest,
    _admin_user: AdminUserDep,
    banner_repo: ExtensionBannerRepositoryDep,
):
    normalized_action_text = payload.action_text.strip() if payload.action_text else None
    normalized_action_url = payload.action_url.strip() if payload.action_url else None
    if normalized_action_text and not normalized_action_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="action_url is required when action_text is set",
        )

    banner = await banner_repo.update_banner(
        title=payload.title.strip(),
        message=payload.message.strip(),
        action_text=normalized_action_text,
        action_url=normalized_action_url,
        is_active=payload.is_active,
    )
    return AdminExtensionBannerResponse(
        title=banner.title,
        message=banner.message,
        action_text=banner.action_text,
        action_url=banner.action_url,
        is_active=banner.is_active,
    )
