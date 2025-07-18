from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api import router as api_router
from .util_router import router as util_router
from app.config import settings

app = FastAPI(title="Anime Stars", description="Unofficial Anime Stars API")
app.include_router(api_router)
app.include_router(util_router)

# Монтуємо статичну директорію для доступу до файлів
app.mount("/static/storage", StaticFiles(directory=settings.storage.path), name="storage")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
