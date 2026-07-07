"""GET /signal/{symbol} (computed fresh) and GET /signals/latest (cached)."""

import asyncio
from typing import cast

import ccxt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.indicators import MIN_CANDLES_FOR_TA, compute_all_indicators
from app.analysis.signal_generator import build_ensemble_signal
from app.api.deps import get_session
from app.core.config import get_settings
from app.data.historical_loader import get_ohlcv
from app.data.symbol_map import resolve_exchange_pair
from app.models.repository import get_latest_signals
from app.schemas.signals import FinalSignal, IndicatorBreakdownOut, SignalOut, SignalsLatestResponse

router = APIRouter()


@router.get("/signal/{symbol}", response_model=SignalOut)
async def get_signal(symbol: str) -> SignalOut:
    """Always computed fresh (no DB read), so it works for any symbol — not
    just whatever made the current top 10."""
    settings = get_settings()
    symbol = symbol.upper()
    pair = resolve_exchange_pair(symbol)
    if pair is None:
        raise HTTPException(status_code=404, detail=f"No exchange mapping for '{symbol}'")

    try:
        candles = await asyncio.to_thread(
            get_ohlcv,
            pair,
            timeframe=settings.candle_timeframe,
            exchange_id=settings.candle_exchange_id,
        )
    except ccxt.BaseError as exc:
        raise HTTPException(
            status_code=404, detail=f"'{symbol}' is not listed on {settings.candle_exchange_id}"
        ) from exc

    if len(candles) < MIN_CANDLES_FOR_TA:
        raise HTTPException(status_code=422, detail=f"Not enough candle history for '{symbol}' yet")

    indicators = compute_all_indicators(candles)
    return build_ensemble_signal(symbol, indicators)


@router.get("/signals/latest", response_model=SignalsLatestResponse)
async def get_latest_signals_route(
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> SignalsLatestResponse:
    run_at, rows = await get_latest_signals(session)
    if run_at is None:
        raise HTTPException(status_code=503, detail="No signal run has completed yet")
    return SignalsLatestResponse(
        run_at=run_at,
        signals=[
            SignalOut(
                symbol=row.symbol,
                final_signal=cast(FinalSignal, row.final_action),
                confidence=row.confidence,
                timestamp=row.run_at,
                breakdown=[IndicatorBreakdownOut(**b) for b in row.breakdown],
            )
            for row in rows
        ],
    )
