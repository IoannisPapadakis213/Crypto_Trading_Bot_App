"""CoinGecko free-tier market data source.

Uses the bulk `/coins/markets` endpoint so the whole top-N universe costs a
single HTTP call. Passing `price_change_percentage=1h,24h,7d` gets the
multi-window % change data in that same call, which the ranking engine's
volatility estimate depends on — the free tier's rate limit (and its
monthly call quota) makes per-coin calls for ~100 assets every 15 minutes
impractical.
"""

import requests

from app.core.config import get_settings
from app.data.sources.base import MarketDataPoint, MarketDataSource, MarketDataSourceError

_TIMEOUT_SECONDS = 15


class CoinGeckoSource(MarketDataSource):
    name = "coingecko"

    def __init__(self) -> None:
        self._settings = get_settings()

    def _headers(self) -> dict[str, str]:
        if self._settings.coingecko_api_key:
            return {"x-cg-demo-api-key": self._settings.coingecko_api_key}
        return {}

    def fetch(self, universe_size: int) -> list[MarketDataPoint]:
        try:
            response = requests.get(
                f"{self._settings.coingecko_base_url}/coins/markets",
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": str(min(universe_size, 250)),
                    "page": "1",
                    "sparkline": "false",
                    "price_change_percentage": "1h,24h,7d",
                },
                headers=self._headers(),
                timeout=_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise MarketDataSourceError(f"CoinGecko request failed: {exc}") from exc

        return [self._to_point(row) for row in response.json()]

    def _to_point(self, row: dict) -> MarketDataPoint:
        return MarketDataPoint(
            source=self.name,
            external_id=row["id"],
            symbol=row["symbol"].upper(),
            name=row["name"],
            price_usd=row["current_price"] or 0.0,
            market_cap=row["market_cap"] or 0.0,
            volume_24h=row["total_volume"] or 0.0,
            market_cap_rank=row["market_cap_rank"],
            pct_change_1h=row.get("price_change_percentage_1h_in_currency"),
            pct_change_24h=row.get("price_change_percentage_24h_in_currency")
            or row.get("price_change_percentage_24h"),
            pct_change_7d=row.get("price_change_percentage_7d_in_currency"),
        )
