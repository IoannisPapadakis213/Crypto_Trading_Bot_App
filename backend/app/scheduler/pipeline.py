"""The pipeline: fetch market data -> store snapshot -> rank -> run TA on the
top N -> store signals. Invoked once immediately and then on a fixed
interval by `jobs.start_scheduler`.
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta

import ccxt
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.analysis.indicators import MIN_CANDLES_FOR_TA, compute_all_indicators
from app.analysis.ranking import rank_assets
from app.analysis.signal_generator import build_ensemble_signal
from app.core.config import Settings
from app.data.aggregator import MarketDataAggregator
from app.data.historical_loader import get_ohlcv
from app.data.sources.base import MarketDataSourceError
from app.data.sources.coingecko import CoinGeckoSource
from app.data.symbol_map import resolve_exchange_pair
from app.models.repository import (
    load_recent_volumes,
    persist_rankings,
    persist_signals,
    persist_snapshot,
)
from app.schemas.signals import SignalOut

logger = logging.getLogger(__name__)

_aggregator = MarketDataAggregator([CoinGeckoSource()])


async def run_pipeline(session_factory: async_sessionmaker, settings: Settings) -> None:
    run_at = datetime.now(UTC)

    try:
        points = await asyncio.to_thread(_aggregator.collect, settings.market_universe_size)
    except MarketDataSourceError:
        logger.exception("Market data fetch failed, skipping this pipeline run")
        return

    async with session_factory() as session:
        await persist_snapshot(session, run_at, points)

    async with session_factory() as session:
        volume_history = await load_recent_volumes(
            session, [p.symbol for p in points], run_at - timedelta(days=7)
        )

    ranked = rank_assets(
        points, volume_history, settings.ranking_top_n, settings.min_snapshots_for_volume_avg
    )

    async with session_factory() as session:
        await persist_rankings(session, run_at, ranked)

    signals: list[SignalOut] = []
    for asset in ranked:
        pair = resolve_exchange_pair(asset.symbol)
        if pair is None:
            logger.info("No exchange mapping for %s, skipping technical analysis", asset.symbol)
            continue
        try:
            candles = await asyncio.to_thread(
                get_ohlcv,
                pair,
                timeframe=settings.candle_timeframe,
                exchange_id=settings.candle_exchange_id,
            )
        except ccxt.BaseError:
            logger.warning(
                "No candle data for %s (%s) on %s", asset.symbol, pair, settings.candle_exchange_id
            )
            continue

        if len(candles) < MIN_CANDLES_FOR_TA:
            logger.info("Not enough candle history for %s (%d rows)", asset.symbol, len(candles))
            continue

        indicators = compute_all_indicators(candles)
        signals.append(build_ensemble_signal(asset.symbol, indicators))

    if signals:
        async with session_factory() as session:
            await persist_signals(session, run_at, signals)
