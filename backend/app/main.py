"""FastAPI application entrypoint.

Local dev: `uvicorn app.main:app --reload` from `backend/`.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import rankings, signals
from app.core.config import get_settings
from app.core.db import init_db
from app.scheduler.jobs import shutdown_scheduler, start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await init_db()
    scheduler = start_scheduler()
    try:
        yield
    finally:
        shutdown_scheduler(scheduler)


app = FastAPI(title="AI Trader — Signal API", lifespan=lifespan)

_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origins_list,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(rankings.router)
app.include_router(signals.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
