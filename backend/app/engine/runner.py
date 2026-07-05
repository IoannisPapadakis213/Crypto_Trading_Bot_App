"""The one loop shared by both the backtester and live paper trading.

`StrategyRunner.process_candle` is called once per newly-closed candle. It
enforces stop-losses first (regardless of what the strategy says this tick),
then asks the strategy for a signal, sizes it via the RiskManager, and
executes through the broker. Backtesting just calls this once per historical
candle; live trading will call it once per candle close from a websocket/
polling feed — same function either way.
"""

import pandas as pd

from app.engine.broker import BrokerBase
from app.engine.risk_manager import RiskManager
from app.strategies.base import Signal, Strategy


class StrategyRunner:
    def __init__(self, strategy: Strategy, broker: BrokerBase, risk_manager: RiskManager) -> None:
        self.strategy = strategy
        self.broker = broker
        self.risk_manager = risk_manager

    def process_candle(self, history: pd.DataFrame) -> Signal | None:
        """`history` is all candles up to and including the newest closed one,
        oldest-first. Returns the strategy's Signal, or None if there isn't
        enough history yet to evaluate the strategy."""
        if len(history) < self.strategy.required_history:
            return None

        last = history.iloc[-1]
        symbol = str(last["symbol"])
        price = float(last["close"])
        timestamp = last["timestamp"]
        prices = {symbol: price}

        for stopped_symbol in self.risk_manager.check_stop_losses(self.broker.portfolio, prices):
            pos = self.broker.portfolio.positions.get(stopped_symbol)
            if pos is not None:
                self.broker.execute(
                    stopped_symbol, "SELL", pos.qty, prices[stopped_symbol], timestamp,
                    strategy_name=self.strategy.name, confidence=1.0,
                )

        signal = self.strategy.on_candle(history)
        qty = self.risk_manager.evaluate(signal, self.broker.portfolio, price)
        if qty > 0:
            self.broker.execute(
                symbol, signal.action, qty, price, timestamp,
                strategy_name=signal.strategy_name, confidence=signal.confidence,
            )

        return signal
