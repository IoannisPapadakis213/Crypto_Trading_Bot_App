"""Combines one or more MarketDataSources into a single top-N universe.

Only CoinGecko is wired in today. To add a second source (Binance, an
on-chain indexer, ...) later: implement `MarketDataSource`, add an instance
to the list passed into `MarketDataAggregator`, and extend `collect`'s merge
policy below — ranking/analysis code never needs to change.
"""

from app.data.sources.base import MarketDataPoint, MarketDataSource


class MarketDataAggregator:
    def __init__(self, sources: list[MarketDataSource]) -> None:
        self._sources = sources

    def collect(self, universe_size: int) -> list[MarketDataPoint]:
        """With one source, this is just that source's output. With more than
        one, entries are merged by `symbol`, first-source-wins (the order of
        `sources` becomes a priority order)."""
        merged: dict[str, MarketDataPoint] = {}
        for source in self._sources:
            for point in source.fetch(universe_size):
                merged.setdefault(point.symbol, point)
        return list(merged.values())[:universe_size]
