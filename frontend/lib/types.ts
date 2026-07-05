// Shapes mirror what the real FastAPI/WebSocket layer will eventually send
// (see backend/app/strategies/base.py::Signal and backend/app/engine/broker.py::Fill),
// so swapping the mock engine for real API/WS calls later shouldn't require
// changing component props — only where the data comes from.

export type Side = "BUY" | "SELL";
export type SignalAction = Side | "HOLD";

export interface Candle {
  time: number; // unix seconds, UTC — lightweight-charts' native format
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Signal {
  id: string;
  action: SignalAction;
  confidence: number; // 0..1
  symbol: string;
  timestamp: number; // unix ms
  strategyName: string;
}

export interface Trade {
  id: string;
  symbol: string;
  side: Side;
  qty: number;
  price: number;
  fee: number;
  timestamp: number; // unix ms
  strategyName: string;
  confidence: number;
}

export interface Position {
  symbol: string;
  qty: number;
  avgEntryPrice: number;
  currentPrice: number;
  unrealizedPnl: number;
  unrealizedPnlPct: number;
}

export interface Portfolio {
  cash: number;
  startingCash: number;
  equity: number;
  positions: Position[];
}

export interface EquityPoint {
  time: number; // unix seconds
  equity: number;
}

export interface StrategyConfig {
  id: string;
  label: string;
  symbol: string;
  isActive: boolean;
  description: string;
  colorVar: string; // CSS custom property name, e.g. "--series-blue"
}

export interface MarketSnapshot {
  symbol: string;
  candles: Candle[];
  portfolio: Portfolio;
  equityCurve: EquityPoint[];
  trades: Trade[];
  signals: Signal[];
  strategies: StrategyConfig[];
}
