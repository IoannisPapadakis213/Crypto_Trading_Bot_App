"""Scores the market universe on momentum, volume spike, and volatility, and
returns the top N.

All functions here are pure (no I/O), mirroring how `RiskManager` stays
separate from persistence in the existing paper-trading engine.

Volume spike needs a 7-day rolling average volume per asset. CoinGecko's
free tier has no affordable bulk endpoint for historical volume across ~100
coins, so that baseline is built from our own accumulated `MarketSnapshot`
rows instead (see `models/repository.load_recent_volumes`). Until enough of
our own history exists for a symbol, its volume-spike score is neutral
(0.5) rather than an error or a guess.
"""

from dataclasses import dataclass
from statistics import fmean

from app.data.sources.base import MarketDataPoint

MOMENTUM_WEIGHT = 0.4
VOLUME_SPIKE_WEIGHT = 0.3
VOLATILITY_WEIGHT = 0.3

_NEUTRAL_SCORE = 0.5


def _clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def compute_momentum_score(pct_change_24h: float | None) -> float:
    if pct_change_24h is None:
        return _NEUTRAL_SCORE
    clipped = _clip(pct_change_24h, -20.0, 20.0)
    return (clipped + 20.0) / 40.0


def compute_volume_spike(
    current_volume: float, historical_volumes: list[float], min_snapshots: int
) -> tuple[float, float | None]:
    """Returns (score in [0, 1], ratio-to-baseline or None if too little history)."""
    if len(historical_volumes) < min_snapshots:
        return _NEUTRAL_SCORE, None
    baseline = fmean(historical_volumes)
    if baseline <= 0:
        return _NEUTRAL_SCORE, None
    ratio = current_volume / baseline
    return _clip(ratio / 3.0, 0.0, 1.0), ratio


def compute_volatility_score(
    pct_1h: float | None, pct_24h: float | None, pct_7d: float | None
) -> float:
    known = [v for v in (pct_1h, pct_24h, pct_7d) if v is not None]
    if len(known) < 2:
        return _NEUTRAL_SCORE
    dispersion = max(known) - min(known)
    return _clip(dispersion / 40.0, 0.0, 1.0)


@dataclass
class RankedAsset:
    symbol: str
    rank: int
    momentum_score: float
    volume_spike_score: float
    volatility_score: float
    composite_score: float
    raw_metrics: dict


def rank_assets(
    points: list[MarketDataPoint],
    historical_volume_by_symbol: dict[str, list[float]],
    top_n: int,
    min_snapshots: int,
    weights: tuple[float, float, float] = (MOMENTUM_WEIGHT, VOLUME_SPIKE_WEIGHT, VOLATILITY_WEIGHT),
) -> list[RankedAsset]:
    momentum_weight, volume_weight, volatility_weight = weights
    scored: list[RankedAsset] = []

    for point in points:
        momentum_score = compute_momentum_score(point.pct_change_24h)
        volume_spike_score, volume_spike_ratio = compute_volume_spike(
            point.volume_24h, historical_volume_by_symbol.get(point.symbol, []), min_snapshots
        )
        volatility_score = compute_volatility_score(
            point.pct_change_1h, point.pct_change_24h, point.pct_change_7d
        )
        composite = (
            momentum_weight * momentum_score
            + volume_weight * volume_spike_score
            + volatility_weight * volatility_score
        )
        raw_metrics = {
            "price_usd": point.price_usd,
            "market_cap": point.market_cap,
            "volume_24h": point.volume_24h,
            "volume_spike_ratio": volume_spike_ratio,
            "pct_change_1h": point.pct_change_1h,
            "pct_change_24h": point.pct_change_24h,
            "pct_change_7d": point.pct_change_7d,
        }
        # rank is a placeholder until the final sort below assigns real ranks
        scored.append(
            RankedAsset(
                symbol=point.symbol,
                rank=0,
                momentum_score=momentum_score,
                volume_spike_score=volume_spike_score,
                volatility_score=volatility_score,
                composite_score=composite,
                raw_metrics=raw_metrics,
            )
        )

    scored.sort(key=lambda asset: asset.composite_score, reverse=True)
    top = scored[:top_n]
    for i, asset in enumerate(top):
        asset.rank = i + 1
    return top
