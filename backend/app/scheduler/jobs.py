"""APScheduler wiring: runs the pipeline once immediately on startup, then
every `settings.pipeline_interval_minutes`.
"""

import logging
from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import Settings, get_settings
from app.core.db import async_session_factory
from app.scheduler.pipeline import run_pipeline

logger = logging.getLogger(__name__)


async def _run_pipeline_job(settings: Settings) -> None:
    try:
        await run_pipeline(async_session_factory, settings)
    except Exception:
        # A failed run must not kill the scheduler thread — it'll retry on
        # the next interval tick.
        logger.exception("Pipeline run failed")


def start_scheduler(settings: Settings | None = None) -> AsyncIOScheduler:
    settings = settings or get_settings()
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        _run_pipeline_job,
        trigger=IntervalTrigger(minutes=settings.pipeline_interval_minutes),
        args=[settings],
        next_run_time=datetime.now(UTC),
        max_instances=1,
        coalesce=True,
        id="market_pipeline",
    )
    scheduler.start()
    return scheduler


def shutdown_scheduler(scheduler: AsyncIOScheduler) -> None:
    scheduler.shutdown(wait=False)
