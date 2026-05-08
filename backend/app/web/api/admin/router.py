from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.config import settings
from app.database.models.user import User
from app.web.auth.deps import UserDep
from app.web.deps import HealthRepositoryDep

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminDatabaseStatsResponse(BaseModel):
    total_cards: int
    total_users: int
    cards_with_stats: int
    cards_stats_today: int


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
