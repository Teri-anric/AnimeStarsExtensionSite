from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.storage.local import LocalStorageService

from .api import router as api_router
from .util_router import router as util_router

app = FastAPI(title="Anime Stars", description="Unofficial Anime Stars API")
app.include_router(api_router)
app.include_router(util_router)

app.mount(
    LocalStorageService.LOCAL_STORAGE_URL,
    StaticFiles(directory=LocalStorageService.LOCAL_STORAGE_PATH, follow_symlink=True),
    name="storage",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
