from fastapi import APIRouter
from pydantic import BaseModel
import time

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


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health():
    start_time = time.time()

    # Calculate total response time (ping)
    ping = (time.time() - start_time) * 1000  # Convert to milliseconds

    # Calculate uptime
    uptime_seconds = time.time() - _app_start_time
    uptime_hours = int(uptime_seconds // 3600)
    uptime_minutes = int((uptime_seconds % 3600) // 60)
    uptime_formatted = f"{uptime_hours}h {uptime_minutes}m"  # TODO: add seconds

    return {
        "status": "healthy",
        "ping": round(ping, 2),
        "uptime_formatted": uptime_formatted,
    }
