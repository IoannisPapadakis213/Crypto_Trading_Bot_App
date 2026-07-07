"""API response shapes for the /rankings endpoint."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class RankingEntryOut(BaseModel):
    model_config = {"from_attributes": True}

    symbol: str
    rank: int
    momentum_score: float
    volume_spike_score: float
    volatility_score: float
    composite_score: float
    raw_metrics: dict[str, Any]


class RankingsResponse(BaseModel):
    run_at: datetime
    entries: list[RankingEntryOut]
