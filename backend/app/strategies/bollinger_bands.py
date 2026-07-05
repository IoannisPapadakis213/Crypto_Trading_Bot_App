"""Bollinger Bands mean-reversion strategy.

Price closing below the lower band is treated as oversold (BUY); closing
above the upper band is treated as overbought (SELL). Confidence scales
with how far price has pushed past the band, relative to band width.
"""

import pandas as pd

from app.strategies.base import Signal, Strategy
from app.strategies.registry import register_strategy


@register_strategy("bollinger_bands")
class BollingerBandsStrategy(Strategy):
    def __init__(self, period: int = 20, num_std: float = 2.0) -> None:
        self.period = period
        self.num_std = num_std
        self.required_history = period + 1

    def on_candle(self, candles: pd.DataFrame) -> Signal:
        if len(candles) < self.required_history:
            return self._hold(candles, reason="insufficient_history")

        close = candles["close"]
        sma = close.rolling(self.period).mean()
        std = close.rolling(self.period).std()
        upper = sma + self.num_std * std
        lower = sma - self.num_std * std

        last = candles.iloc[-1]
        price = float(last["close"])
        upper_now, lower_now = float(upper.iloc[-1]), float(lower.iloc[-1])
        band_width = upper_now - lower_now

        if band_width <= 0:
            return self._hold(candles, reason="zero_band_width")

        if price < lower_now:
            action = "BUY"
            confidence = min(1.0, (lower_now - price) / band_width + 0.2)
        elif price > upper_now:
            action = "SELL"
            confidence = min(1.0, (price - upper_now) / band_width + 0.2)
        else:
            action = "HOLD"
            confidence = 0.0

        return Signal(
            action=action,
            confidence=confidence,
            symbol=str(last["symbol"]),
            timestamp=last["timestamp"],
            strategy_name=self.name,
            metadata={"upper_band": upper_now, "lower_band": lower_now, "sma": float(sma.iloc[-1])},
        )
