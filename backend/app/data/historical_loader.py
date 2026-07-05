"""Historical OHLCV loading with a local Parquet cache.

Fetches candles from an exchange via ccxt and caches them to
`backend/data/historical/{symbol}/{timeframe}.parquet` so repeated backtests
don't re-hit the exchange API. Cache reads use whatever is on disk; if the
requested range extends past what's cached, the gap is fetched and merged in.
"""

from datetime import UTC, datetime
from pathlib import Path

import ccxt
import pandas as pd

CACHE_DIR = Path(__file__).resolve().parents[2] / "data" / "historical"
DEFAULT_EXCHANGE = "kraken"

_OHLCV_COLUMNS = ["timestamp_ms", "open", "high", "low", "close", "volume"]


def _cache_path(exchange_id: str, symbol: str, timeframe: str) -> Path:
    safe_symbol = symbol.replace("/", "_")
    return CACHE_DIR / exchange_id / safe_symbol / f"{timeframe}.parquet"


def _to_ms(dt: datetime) -> int:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return int(dt.timestamp() * 1000)


def _fetch_range(
    exchange: ccxt.Exchange, symbol: str, timeframe: str, since_ms: int, until_ms: int
) -> pd.DataFrame:
    timeframe_ms = exchange.parse_timeframe(timeframe) * 1000
    rows: list[list[float]] = []
    cursor = since_ms
    limit = 1000

    while cursor < until_ms:
        batch = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=cursor, limit=limit)
        if not batch:
            break
        rows.extend(batch)
        last_ts = batch[-1][0]
        next_cursor = last_ts + timeframe_ms
        if next_cursor <= cursor:
            break
        cursor = next_cursor
        if len(batch) < limit:
            break

    if not rows:
        return pd.DataFrame(columns=_OHLCV_COLUMNS)

    df = pd.DataFrame(rows, columns=_OHLCV_COLUMNS)
    return df[(df["timestamp_ms"] >= since_ms) & (df["timestamp_ms"] < until_ms)]


def get_ohlcv(
    symbol: str,
    timeframe: str = "1h",
    since: datetime | None = None,
    until: datetime | None = None,
    exchange_id: str = DEFAULT_EXCHANGE,
    refresh: bool = False,
) -> pd.DataFrame:
    """Return OHLCV candles for `symbol` between `since` and `until` (default
    until=now), fetching only what's missing from the on-disk Parquet cache.

    Returns a DataFrame with columns: timestamp, symbol, open, high, low,
    close, volume — sorted ascending, deduplicated by timestamp.
    """
    until = until or datetime.now(UTC)
    since = since or (until - pd.Timedelta(days=365))
    since_ms, until_ms = _to_ms(since), _to_ms(until)

    path = _cache_path(exchange_id, symbol, timeframe)
    cached = pd.DataFrame(columns=_OHLCV_COLUMNS)
    if path.exists() and not refresh:
        cached = pd.read_parquet(path)

    have_range = (
        not cached.empty
        and cached["timestamp_ms"].min() <= since_ms
        and cached["timestamp_ms"].max() >= until_ms
    )

    if refresh or not have_range:
        exchange_cls = getattr(ccxt, exchange_id)
        exchange = exchange_cls({"enableRateLimit": True})
        fetch_since = since_ms if refresh else min(since_ms, int(cached["timestamp_ms"].min()) if not cached.empty else since_ms)
        fresh = _fetch_range(exchange, symbol, timeframe, fetch_since, until_ms)
        combined = pd.concat([cached, fresh], ignore_index=True)
        combined = combined.drop_duplicates(subset="timestamp_ms").sort_values("timestamp_ms")
        path.parent.mkdir(parents=True, exist_ok=True)
        combined.to_parquet(path, index=False)
        cached = combined

    window = cached[(cached["timestamp_ms"] >= since_ms) & (cached["timestamp_ms"] < until_ms)].copy()
    window["timestamp"] = pd.to_datetime(window["timestamp_ms"], unit="ms", utc=True)
    window["symbol"] = symbol
    window = window.sort_values("timestamp").reset_index(drop=True)
    return window[["timestamp", "symbol", "open", "high", "low", "close", "volume"]]
