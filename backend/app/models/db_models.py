"""ORM tables for persisted pipeline output.

One row per pipeline run per symbol, so `/rankings` and `/signals/latest`
can just query the most recent `run_at` without re-running the pipeline,
and `MarketSnapshot` accumulates the raw history the ranking engine's 7-day
volume-spike baseline is built from (see `analysis.ranking`).
"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"
    __table_args__ = (Index("ix_market_snapshots_symbol_fetched_at", "symbol", "fetched_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    coingecko_id: Mapped[str] = mapped_column(String(64))
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    price_usd: Mapped[float] = mapped_column(Float)
    market_cap: Mapped[float] = mapped_column(Float)
    volume_24h: Mapped[float] = mapped_column(Float)
    market_cap_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pct_change_1h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pct_change_24h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pct_change_7d: Mapped[float | None] = mapped_column(Float, nullable=True)


class Ranking(Base):
    __tablename__ = "rankings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    rank: Mapped[int] = mapped_column(Integer)
    momentum_score: Mapped[float] = mapped_column(Float)
    volume_spike_score: Mapped[float] = mapped_column(Float)
    volatility_score: Mapped[float] = mapped_column(Float)
    composite_score: Mapped[float] = mapped_column(Float)
    raw_metrics: Mapped[dict] = mapped_column(JSON)


class SignalRecord(Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    final_action: Mapped[str] = mapped_column(String(10))
    confidence: Mapped[float] = mapped_column(Float)
    breakdown: Mapped[list] = mapped_column(JSON)
