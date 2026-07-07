"""API response shapes for /signal/{symbol} and /signals/latest.

Also the shape produced internally by `analysis.signal_generator` — one
schema serves both the ensemble logic's return type and the API response,
so there's no separate translation step.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

IndicatorSignal = Literal["BUY", "SELL", "NEUTRAL"]
FinalSignal = Literal["BUY", "SELL", "HOLD"]


class IndicatorBreakdownOut(BaseModel):
    indicator: str
    signal: IndicatorSignal
    values: dict[str, float | None]


class SignalOut(BaseModel):
    symbol: str
    final_signal: FinalSignal
    confidence: float
    timestamp: datetime
    breakdown: list[IndicatorBreakdownOut]


class SignalsLatestResponse(BaseModel):
    run_at: datetime
    signals: list[SignalOut]
