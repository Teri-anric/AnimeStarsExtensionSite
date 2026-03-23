import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.json_logging import configure_json_app_logging

from .http_audit_middleware import HttpAuditLogMiddleware

configure_json_app_logging(settings.log_json)

from .api import router as api_router
from .util_router import router as util_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from app.database.connection import get_engine
    from app.database.metrics import instrument_engine, start_metrics_background_task

    engine = get_engine()
    instrument_engine(engine)
    metrics_task = start_metrics_background_task(engine)
    yield
    metrics_task.cancel()
    try:
        await metrics_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Anime Stars",
    description="Unofficial Anime Stars API",
    lifespan=lifespan,
)
Instrumentator().instrument(app).expose(app, include_in_schema=False)
app.include_router(api_router)
app.include_router(util_router)

app.add_middleware(
    HttpAuditLogMiddleware,
    enabled=settings.log_http_bodies,
    max_bytes=settings.log_http_body_max_bytes,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
