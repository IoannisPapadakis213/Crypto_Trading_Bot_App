"""Async SQLAlchemy engine/session setup.

SQLite today; swapping `DATABASE_URL` to Postgres later needs no code
changes here — the WAL pragma below is skipped for any non-SQLite URL, and
every model uses plain `sqlalchemy.JSON` rather than a Postgres-only type.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    # Imported here (not at module load) so `Base.metadata` is fully
    # populated with every table before `create_all` runs, without this
    # module having to import the models package (which imports Base from
    # here — importing it at the top would be circular).
    from app.models import db_models  # noqa: F401

    async with engine.begin() as conn:
        if settings.database_url.startswith("sqlite"):
            # Reduces writer/reader lock contention between the scheduler's
            # periodic writes and concurrent API reads.
            await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session
