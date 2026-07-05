"""Shared order-execution simulation.

`BrokerBase` implements the actual fill/ledger logic (slippage, fees,
position/cash updates) once. `SimulatedBroker` (used by the backtester) is
just that logic running in-memory. Phase 2's `PaperBroker` (live paper
trading) will subclass this and override `_on_fill` to persist to Postgres
— the execution math itself doesn't change between backtest and live,
which is the point: a strategy that back tests well runs through the exact
same fill logic live.

Known simplification: orders always fill immediately in full at a slippage-
adjusted price; there is no simulated order-book depth.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

Side = Literal["BUY", "SELL"]


@dataclass
class Position:
    symbol: str
    qty: float
    avg_entry_price: float


@dataclass
class Fill:
    symbol: str
    side: Side
    qty: float
    price: float
    fee: float
    timestamp: datetime
    strategy_name: str
    signal_confidence: float


@dataclass
class PortfolioState:
    cash: float
    starting_cash: float
    positions: dict[str, Position] = field(default_factory=dict)
    trades: list[Fill] = field(default_factory=list)

    def equity(self, mark_prices: dict[str, float]) -> float:
        total = self.cash
        for symbol, pos in self.positions.items():
            total += pos.qty * mark_prices.get(symbol, pos.avg_entry_price)
        return total


@dataclass
class ExecutionConfig:
    slippage_bps: float = 5.0
    fee_bps: float = 10.0


class BrokerBase:
    def __init__(
        self, portfolio: PortfolioState, execution_config: ExecutionConfig | None = None
    ) -> None:
        self.portfolio = portfolio
        self.execution_config = execution_config or ExecutionConfig()

    def _fill_price(self, side: Side, reference_price: float) -> float:
        direction = 1 if side == "BUY" else -1
        return reference_price * (1 + direction * self.execution_config.slippage_bps / 10_000)

    def execute(
        self,
        symbol: str,
        side: Side,
        qty: float,
        reference_price: float,
        timestamp: datetime,
        strategy_name: str,
        confidence: float,
    ) -> Fill | None:
        if qty <= 0:
            return None

        fill_price = self._fill_price(side, reference_price)
        notional = fill_price * qty
        fee = notional * self.execution_config.fee_bps / 10_000

        if side == "BUY":
            cost = notional + fee
            if cost > self.portfolio.cash:
                return None
            self.portfolio.cash -= cost
            existing = self.portfolio.positions.get(symbol)
            if existing is None:
                self.portfolio.positions[symbol] = Position(symbol, qty, fill_price)
            else:
                new_qty = existing.qty + qty
                existing.avg_entry_price = (
                    existing.avg_entry_price * existing.qty + fill_price * qty
                ) / new_qty
                existing.qty = new_qty
        else:
            existing = self.portfolio.positions.get(symbol)
            if existing is None or existing.qty < qty - 1e-12:
                return None
            proceeds = notional - fee
            self.portfolio.cash += proceeds
            existing.qty -= qty
            if existing.qty <= 1e-12:
                del self.portfolio.positions[symbol]

        fill = Fill(
            symbol=symbol,
            side=side,
            qty=qty,
            price=fill_price,
            fee=fee,
            timestamp=timestamp,
            strategy_name=strategy_name,
            signal_confidence=confidence,
        )
        self.portfolio.trades.append(fill)
        self._on_fill(fill)
        return fill

    def _on_fill(self, fill: Fill) -> None:
        """Extension point for subclasses that need to persist fills. No-op here."""


class SimulatedBroker(BrokerBase):
    """In-memory broker used by the backtester — no persistence."""
