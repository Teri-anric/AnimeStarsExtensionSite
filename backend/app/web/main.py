from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router
from .util_router import router as util_router

app = FastAPI(title="Anime Stars", description="Unofficial Anime Stars API")
app.include_router(api_router)
app.include_router(util_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
