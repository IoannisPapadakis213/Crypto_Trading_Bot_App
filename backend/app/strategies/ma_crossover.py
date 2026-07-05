"""Moving-average crossover strategy.

Classic trend-following signal: go long when the fast moving average
crosses above the slow one, go short/flat when it crosses back below.
Confidence scales with how far apart the two averages are, normalized by
price, so a decisive cross carries more weight than a marginal one.
"""

import pandas as pd

from app.strategies.base import Signal, Strategy
from app.strategies.registry import register_strategy


@register_strategy("ma_crossover")
class MovingAverageCrossoverStrategy(Strategy):
    def __init__(self, fast_period: int = 10, slow_period: int = 30) -> None:
        if fast_period >= slow_period:
            raise ValueError("fast_period must be smaller than slow_period")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.required_history = slow_period + 1

    def on_candle(self, candles: pd.DataFrame) -> Signal:
        close = candles["close"]
        fast = close.rolling(self.fast_period).mean()
        slow = close.rolling(self.slow_period).mean()

        if len(candles) < self.required_history or fast.isna().iloc[-1] or slow.isna().iloc[-1]:
            return self._hold(candles, reason="insufficient_history")

        fast_now, fast_prev = fast.iloc[-1], fast.iloc[-2]
        slow_now, slow_prev = slow.iloc[-1], slow.iloc[-2]
        last = candles.iloc[-1]

        crossed_up = fast_prev <= slow_prev and fast_now > slow_now
        crossed_down = fast_prev >= slow_prev and fast_now < slow_now
        spread = abs(fast_now - slow_now) / last["close"] if last["close"] else 0.0
        confidence = min(1.0, spread * 20)

        if crossed_up:
            action = "BUY"
        elif crossed_down:
            action = "SELL"
        else:
            action = "HOLD"
            confidence = 0.0

        return Signal(
            action=action,
            confidence=confidence,
            symbol=str(last["symbol"]),
            timestamp=last["timestamp"],
            strategy_name=self.name,
            metadata={"fast_ma": float(fast_now), "slow_ma": float(slow_now)},
        )
