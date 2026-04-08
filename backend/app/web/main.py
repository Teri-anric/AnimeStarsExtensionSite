import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest, multiprocess
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.json_logging import configure_json_app_logging

from .api import router as api_router
from .http_audit_middleware import HttpAuditLogMiddleware
from .util_router import router as util_router

configure_json_app_logging(settings.log_json)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from app.database.connection import get_engine
    from app.database.metrics import instrument_engine, start_metrics_background_task
    from app.redis_client import close_redis

    engine = get_engine()
    instrument_engine(engine)
    metrics_task = start_metrics_background_task(engine)
    yield
    metrics_task.cancel()
    try:
        await metrics_task
    except asyncio.CancelledError:
        pass
    await close_redis()


app = FastAPI(
    title="Anime Stars",
    description="Unofficial Anime Stars API",
    lifespan=lifespan,
)
Instrumentator().instrument(app)
app.include_router(api_router)
app.include_router(util_router)


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    multiproc_dir = os.getenv("PROMETHEUS_MULTIPROC_DIR")
    if multiproc_dir:
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        return Response(content=generate_latest(registry), media_type=CONTENT_TYPE_LATEST)

    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

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
