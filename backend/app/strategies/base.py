"""Core strategy abstraction.

A Strategy only expresses a directional opinion (BUY/SELL/HOLD) about a
symbol given its recent candle history. It never decides position size,
never touches the portfolio, and never places orders — that separation is
deliberate: sizing/risk lives in RiskManager, execution lives in the broker.
This keeps strategies trivially testable and swappable.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Literal

import pandas as pd
from pydantic import BaseModel, Field

SignalAction = Literal["BUY", "SELL", "HOLD"]


class Signal(BaseModel):
    action: SignalAction
    confidence: float = Field(ge=0.0, le=1.0)
    symbol: str
    timestamp: datetime
    strategy_name: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Strategy(ABC):
    """Base class for all trading strategies.

    Subclasses implement `on_candle`, which is called once per closed
    candle with the full available history (oldest-first) and must return
    a Signal. `required_history` tells the runner/backtester how many
    candles must exist before the first call is made.
    """

    name: str
    required_history: int = 2

    def warm_up(self, candles: pd.DataFrame) -> None:
        """Optional hook for stateful strategies to initialize internal state
        from history before live evaluation begins. No-op by default."""

    @abstractmethod
    def on_candle(self, candles: pd.DataFrame) -> Signal:
        """Evaluate the strategy against `candles` (columns: timestamp, symbol,
        open, high, low, close, volume; oldest row first, last row is the most
        recently closed candle) and return a Signal for the last timestamp."""
        raise NotImplementedError

    def _hold(self, candles: pd.DataFrame, **metadata: Any) -> Signal:
        last = candles.iloc[-1]
        return Signal(
            action="HOLD",
            confidence=0.0,
            symbol=str(last["symbol"]),
            timestamp=last["timestamp"],
            strategy_name=self.name,
            metadata=metadata,
        )
