"""Five technical indicators computed with pandas-ta-classic, each reduced to
a BUY/SELL/NEUTRAL opinion so the signal generator can combine them
uniformly.

Column names below were confirmed against a real, installed 0.6.52 run (not
assumed from memory) against BTC/USD daily candles pulled via
`historical_loader.get_ohlcv` — they're version-sensitive and worth
re-checking if pandas-ta-classic is ever upgraded across a minor version.
"""

from dataclasses import dataclass
from typing import Literal

import pandas as pd
import pandas_ta_classic as ta

IndicatorSignal = Literal["BUY", "SELL", "NEUTRAL"]

RSI_PERIOD = 14
RSI_OVERSOLD = 30.0
RSI_OVERBOUGHT = 70.0

MACD_FAST, MACD_SLOW, MACD_SIGNAL = 12, 26, 9

BB_PERIOD = 20
BB_STD = 2.0

MA_FAST, MA_SLOW = 50, 200

ICHIMOKU_TENKAN, ICHIMOKU_KIJUN, ICHIMOKU_SENKOU = 9, 26, 52

# The tightest lookback requirement of the five is MA_SLOW; a small buffer
# avoids edge-of-window NaNs in the other four.
MIN_CANDLES_FOR_TA = MA_SLOW + 10


@dataclass
class IndicatorResult:
    name: str
    signal: IndicatorSignal
    values: dict[str, float | None]


def _safe_float(value: object) -> float | None:
    return float(value) if pd.notna(value) else None  # type: ignore[arg-type]


def compute_rsi(candles: pd.DataFrame) -> IndicatorResult:
    rsi = ta.rsi(candles["close"], length=RSI_PERIOD)
    latest = _safe_float(rsi.iloc[-1])
    if latest is None:
        signal: IndicatorSignal = "NEUTRAL"
    elif latest < RSI_OVERSOLD:
        signal = "BUY"
    elif latest > RSI_OVERBOUGHT:
        signal = "SELL"
    else:
        signal = "NEUTRAL"
    return IndicatorResult(name="rsi", signal=signal, values={"rsi": latest})


def compute_macd(candles: pd.DataFrame) -> IndicatorResult:
    macd = ta.macd(candles["close"], fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL)
    macd_line = _safe_float(macd[f"MACD_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"].iloc[-1])
    signal_line = _safe_float(macd[f"MACDs_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"].iloc[-1])
    histogram = _safe_float(macd[f"MACDh_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"].iloc[-1])

    if histogram is None:
        signal: IndicatorSignal = "NEUTRAL"
    elif histogram > 0:
        signal = "BUY"
    elif histogram < 0:
        signal = "SELL"
    else:
        signal = "NEUTRAL"
    return IndicatorResult(
        name="macd",
        signal=signal,
        values={"macd": macd_line, "signal_line": signal_line, "histogram": histogram},
    )


def compute_bbands(candles: pd.DataFrame) -> IndicatorResult:
    bb = ta.bbands(candles["close"], length=BB_PERIOD, std=BB_STD)
    price = _safe_float(candles["close"].iloc[-1])
    lower = _safe_float(bb[f"BBL_{BB_PERIOD}_{BB_STD}"].iloc[-1])
    upper = _safe_float(bb[f"BBU_{BB_PERIOD}_{BB_STD}"].iloc[-1])

    if price is None or lower is None or upper is None:
        signal: IndicatorSignal = "NEUTRAL"
    elif price <= lower:
        signal = "BUY"
    elif price >= upper:
        signal = "SELL"
    else:
        signal = "NEUTRAL"
    values = {"price": price, "lower": lower, "upper": upper}
    return IndicatorResult(name="bollinger_bands", signal=signal, values=values)


def compute_ma_crossover(candles: pd.DataFrame) -> IndicatorResult:
    fast_series = ta.sma(candles["close"], length=MA_FAST)
    slow_series = ta.sma(candles["close"], length=MA_SLOW)
    fast = _safe_float(fast_series.iloc[-1])
    slow = _safe_float(slow_series.iloc[-1])

    # Current relative position, not just the instantaneous crossing tick —
    # each pipeline run needs a standalone signal, not "did a cross happen
    # on this exact candle."
    if fast is None or slow is None:
        signal: IndicatorSignal = "NEUTRAL"
    elif fast > slow:
        signal = "BUY"
    elif fast < slow:
        signal = "SELL"
    else:
        signal = "NEUTRAL"
    return IndicatorResult(
        name="ma_crossover", signal=signal, values={"ma_fast": fast, "ma_slow": slow}
    )


def compute_ichimoku(candles: pd.DataFrame) -> IndicatorResult:
    ichimoku_df, _ = ta.ichimoku(
        candles["high"], candles["low"], candles["close"],
        tenkan=ICHIMOKU_TENKAN, kijun=ICHIMOKU_KIJUN, senkou=ICHIMOKU_SENKOU,
    )
    price = _safe_float(candles["close"].iloc[-1])
    span_a = _safe_float(ichimoku_df[f"ISA_{ICHIMOKU_TENKAN}"].iloc[-1])
    span_b = _safe_float(ichimoku_df[f"ISB_{ICHIMOKU_KIJUN}"].iloc[-1])

    if price is None or span_a is None or span_b is None:
        signal: IndicatorSignal = "NEUTRAL"
    else:
        cloud_top, cloud_bottom = max(span_a, span_b), min(span_a, span_b)
        if price > cloud_top:
            signal = "BUY"
        elif price < cloud_bottom:
            signal = "SELL"
        else:
            signal = "NEUTRAL"
    return IndicatorResult(
        name="ichimoku", signal=signal, values={"price": price, "span_a": span_a, "span_b": span_b}
    )


_INDICATOR_FUNCS = [
    compute_rsi, compute_macd, compute_bbands, compute_ma_crossover, compute_ichimoku,
]


def compute_all_indicators(candles: pd.DataFrame) -> list[IndicatorResult]:
    """`candles` needs columns open/high/low/close/volume, oldest-first, with
    at least `MIN_CANDLES_FOR_TA` rows — callers are responsible for that
    check (MA_SLOW is the binding constraint)."""
    return [fn(candles) for fn in _INDICATOR_FUNCS]
