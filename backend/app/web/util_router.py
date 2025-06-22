from fastapi import APIRouter
from pydantic import BaseModel
import time
from .deps import HealthRepositoryDep

router = APIRouter()

# Store the application start time
_app_start_time = time.time()

@router.get("/")
def read_root():
    return {"message": "Hello, World!"}


class HealthResponse(BaseModel):
    status: str
    ping: float
    uptime_formatted: str
    database_stats: dict


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health(health_repo: HealthRepositoryDep):
    start_time = time.time()
    
    # Get database stats
    total_cards_count = await health_repo.get_total_cards_count()
    total_users_count = await health_repo.get_total_users_count()
    total_cards_with_stats_count = await health_repo.get_total_cards_with_stats_count()
    total_cards_stats_today_count = await health_repo.get_total_cards_stats_today_count()
    
    # Calculate total response time (ping)
    ping = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Calculate uptime
    uptime_seconds = time.time() - _app_start_time
    uptime_hours = int(uptime_seconds // 3600)
    uptime_minutes = int((uptime_seconds % 3600) // 60)
    uptime_formatted = f"{uptime_hours}h {uptime_minutes}m"     # TODO: add seconds 
    
    return {
        "status": "healthy",
        "ping": round(ping, 2),
        "uptime_formatted": uptime_formatted,
        "database_stats": {
            "total_cards": total_cards_count,
            "total_users": total_users_count,
            "cards_with_stats": total_cards_with_stats_count,
            "cards_stats_today": total_cards_stats_today_count,
        }
    }
