"""Position sizing and risk limits.

Strategies only emit directional opinions (see app/strategies/base.py); this
module decides how much to actually trade, and can veto a signal entirely.
Keeping it separate means risk rules are visible and testable on their own,
independent of any particular strategy's logic.

Simplifications, documented rather than hidden: only one open lot per
symbol is allowed (a BUY signal while already holding is ignored rather than
pyramiding), and a SELL signal always exits the full position.
"""

from dataclasses import dataclass
from datetime import date, datetime

from app.engine.broker import PortfolioState
from app.strategies.base import Signal


@dataclass
class RiskConfig:
    max_position_pct: float = 0.10
    max_concurrent_positions: int = 5
    stop_loss_pct: float = 0.05
    max_daily_drawdown_pct: float = 0.05


class RiskManager:
    def __init__(self, config: RiskConfig | None = None) -> None:
        self.config = config or RiskConfig()
        self._day: date | None = None
        self._equity_at_day_start: float | None = None
        self._trading_halted_today = False

    def _refresh_day(self, timestamp: datetime, equity: float) -> None:
        day = timestamp.date()
        if self._day != day:
            self._day = day
            self._equity_at_day_start = equity
            self._trading_halted_today = False

    def check_stop_losses(
        self, portfolio: PortfolioState, prices: dict[str, float]
    ) -> list[str]:
        """Return symbols whose open position has breached the stop-loss %,
        so the caller can force an exit regardless of what the strategy says."""
        triggered = []
        for symbol, pos in portfolio.positions.items():
            price = prices.get(symbol)
            if price is None or pos.avg_entry_price <= 0:
                continue
            loss_pct = (pos.avg_entry_price - price) / pos.avg_entry_price
            if loss_pct >= self.config.stop_loss_pct:
                triggered.append(symbol)
        return triggered

    def evaluate(self, signal: Signal, portfolio: PortfolioState, price: float) -> float:
        """Return the quantity to trade for this signal (0.0 means don't trade)."""
        equity = portfolio.equity({signal.symbol: price})
        self._refresh_day(signal.timestamp, equity)

        if self._equity_at_day_start and self._equity_at_day_start > 0:
            drawdown = (self._equity_at_day_start - equity) / self._equity_at_day_start
            if drawdown >= self.config.max_daily_drawdown_pct:
                self._trading_halted_today = True

        if signal.action == "HOLD" or price <= 0:
            return 0.0

        if signal.action == "BUY":
            if self._trading_halted_today:
                return 0.0
            if signal.symbol in portfolio.positions:
                return 0.0
            if len(portfolio.positions) >= self.config.max_concurrent_positions:
                return 0.0
            allocation = min(equity * self.config.max_position_pct * signal.confidence, portfolio.cash)
            return allocation / price if allocation > 0 else 0.0

        if signal.action == "SELL":
            pos = portfolio.positions.get(signal.symbol)
            return pos.qty if pos else 0.0

        return 0.0
