"""Maps a CoinGecko ticker symbol to a ccxt trading pair on the configured
exchange (Kraken by default).

ccxt already normalizes exchange-specific quirks (e.g. Kraken's raw `XBT`)
into unified symbols like `BTC/USD`, so a naive `f"{symbol}/{quote}"` covers
most assets. A few tickers still need an explicit override (either a
different pair name, or `None` to mark them as known-unlisted rather than
letting the naive guess hit ccxt's error path every run). Callers must still
handle `ccxt.BadSymbol`/`ccxt.BaseError` for anything not covered here, since
most of the CoinGecko top-100 simply won't trade on Kraken.
"""

_OVERRIDES: dict[str, str | None] = {
    "MIOTA": "IOTA/USD",
}


def resolve_exchange_pair(symbol: str, quote: str = "USD") -> str | None:
    symbol = symbol.upper()
    if symbol in _OVERRIDES:
        return _OVERRIDES[symbol]
    return f"{symbol}/{quote}"
