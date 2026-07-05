"""RSI mean-reversion strategy.

Computes Wilder's RSI and treats extremes as reversion opportunities: RSI
below the oversold threshold suggests a bounce (BUY), RSI above the
overbought threshold suggests a pullback (SELL). Confidence scales with how
far RSI has pushed past the threshold.
"""

import pandas as pd

from app.strategies.base import Signal, Strategy
from app.strategies.registry import register_strategy


def _wilder_rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)


@register_strategy("rsi_mean_reversion")
class RsiMeanReversionStrategy(Strategy):
    def __init__(
        self, period: int = 14, oversold: float = 30.0, overbought: float = 70.0
    ) -> None:
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.required_history = period + 1

    def on_candle(self, candles: pd.DataFrame) -> Signal:
        if len(candles) < self.required_history:
            return self._hold(candles, reason="insufficient_history")

        rsi = _wilder_rsi(candles["close"], self.period)
        rsi_now = float(rsi.iloc[-1])
        last = candles.iloc[-1]

        if rsi_now <= self.oversold:
            action = "BUY"
            confidence = min(1.0, (self.oversold - rsi_now) / self.oversold + 0.2)
        elif rsi_now >= self.overbought:
            action = "SELL"
            confidence = min(1.0, (rsi_now - self.overbought) / (100 - self.overbought) + 0.2)
        else:
            action = "HOLD"
            confidence = 0.0

        return Signal(
            action=action,
            confidence=confidence,
            symbol=str(last["symbol"]),
            timestamp=last["timestamp"],
            strategy_name=self.name,
            metadata={"rsi": rsi_now},
        )
