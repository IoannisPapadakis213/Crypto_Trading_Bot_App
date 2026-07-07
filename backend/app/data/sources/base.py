"""Interface every market-data source must implement.

The aggregator only talks to this interface, so adding Binance or an
on-chain source later is a matter of writing one more class here and
registering it in `aggregator.py` — no changes needed to ranking/analysis.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class MarketDataPoint(BaseModel):
    source: str
    external_id: str
    symbol: str
    name: str
    price_usd: float
    market_cap: float
    volume_24h: float
    market_cap_rank: int | None
    pct_change_1h: float | None
    pct_change_24h: float | None
    pct_change_7d: float | None


class MarketDataSourceError(Exception):
    """Raised when a source can't be fetched (network error, non-2xx, etc.)."""


class MarketDataSource(ABC):
    name: str

    @abstractmethod
    def fetch(self, universe_size: int) -> list[MarketDataPoint]:
        """Return up to `universe_size` assets ordered by market cap descending.

        Synchronous by design, matching `historical_loader.get_ohlcv` — async
        callers are expected to offload this via `asyncio.to_thread`.
        """
        raise NotImplementedError
