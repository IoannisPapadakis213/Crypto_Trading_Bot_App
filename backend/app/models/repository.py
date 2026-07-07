"""Persistence + query helpers used by the scheduler pipeline and the API
routes. Keeps raw SQLAlchemy usage out of both callers.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.ranking import RankedAsset
from app.data.sources.base import MarketDataPoint
from app.models.db_models import MarketSnapshot, Ranking, SignalRecord
from app.schemas.signals import SignalOut


async def persist_snapshot(
    session: AsyncSession, run_at: datetime, points: list[MarketDataPoint]
) -> None:
    session.add_all(
        MarketSnapshot(
            fetched_at=run_at,
            coingecko_id=p.external_id,
            symbol=p.symbol,
            price_usd=p.price_usd,
            market_cap=p.market_cap,
            volume_24h=p.volume_24h,
            market_cap_rank=p.market_cap_rank,
            pct_change_1h=p.pct_change_1h,
            pct_change_24h=p.pct_change_24h,
            pct_change_7d=p.pct_change_7d,
        )
        for p in points
    )
    await session.commit()


async def load_recent_volumes(
    session: AsyncSession, symbols: list[str], since: datetime
) -> dict[str, list[float]]:
    """Per-symbol volume_24h history from our own snapshots, oldest-first,
    used as the 7-day baseline for volume-spike scoring (see
    `analysis.ranking`)."""
    result = await session.execute(
        select(MarketSnapshot.symbol, MarketSnapshot.volume_24h, MarketSnapshot.fetched_at)
        .where(MarketSnapshot.symbol.in_(symbols))
        .where(MarketSnapshot.fetched_at >= since)
        .order_by(MarketSnapshot.fetched_at.asc())
    )
    history: dict[str, list[float]] = {}
    for symbol, volume, _fetched_at in result.all():
        history.setdefault(symbol, []).append(volume)
    return history


async def persist_rankings(
    session: AsyncSession, run_at: datetime, ranked: list[RankedAsset]
) -> None:
    session.add_all(
        Ranking(
            run_at=run_at,
            symbol=r.symbol,
            rank=r.rank,
            momentum_score=r.momentum_score,
            volume_spike_score=r.volume_spike_score,
            volatility_score=r.volatility_score,
            composite_score=r.composite_score,
            raw_metrics=r.raw_metrics,
        )
        for r in ranked
    )
    await session.commit()


async def persist_signals(
    session: AsyncSession, run_at: datetime, signals: list[SignalOut]
) -> None:
    session.add_all(
        SignalRecord(
            run_at=run_at,
            symbol=s.symbol,
            final_action=s.final_signal,
            confidence=s.confidence,
            breakdown=[b.model_dump() for b in s.breakdown],
        )
        for s in signals
    )
    await session.commit()


async def get_latest_rankings(session: AsyncSession) -> list[Ranking]:
    latest_run = await session.scalar(
        select(Ranking.run_at).order_by(Ranking.run_at.desc()).limit(1)
    )
    if latest_run is None:
        return []
    result = await session.execute(
        select(Ranking).where(Ranking.run_at == latest_run).order_by(Ranking.rank)
    )
    return list(result.scalars().all())


async def get_latest_signals(
    session: AsyncSession,
) -> tuple[datetime | None, list[SignalRecord]]:
    latest_run = await session.scalar(
        select(SignalRecord.run_at).order_by(SignalRecord.run_at.desc()).limit(1)
    )
    if latest_run is None:
        return None, []
    result = await session.execute(select(SignalRecord).where(SignalRecord.run_at == latest_run))
    return latest_run, list(result.scalars().all())
