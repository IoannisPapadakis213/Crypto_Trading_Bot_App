// Client-side stand-in for the real backend (backend/app/engine/runner.py +
// broker.py + risk_manager.py) so the dashboard has something live to render
// before the API exists. It deliberately mirrors that design — a simplified
// SMA crossover evaluated on each finalized candle, sized at 10% of equity,
// one open lot at a time, slippage + fee on fills — so swapping this engine
// for real WebSocket data later is a data-source change, not a UI rewrite.
// This is NOT a trading strategy recommendation; it's a visual simulation.

import type {
  Candle,
  EquityPoint,
  MarketSnapshot,
  Position,
  Signal,
  StrategyConfig,
  Trade,
} from "./types";

const SYMBOL = "BTC/USD";
const STARTING_PRICE = 67_000;
const STARTING_CASH = 100_000;
const SECONDS_PER_CANDLE = 6;
const MAX_CANDLES = 240;
const MAX_EQUITY_POINTS = 480;
const MAX_FEED_ITEMS = 40;
// Deliberately short/twitchy relative to a real strategy (real ones use 10/30
// on hourly candles) so a demo visitor sees a signal within the first minute
// instead of waiting out a rare real crossover.
const FAST_PERIOD = 5;
const SLOW_PERIOD = 15;

export const STRATEGIES: StrategyConfig[] = [
  {
    id: "ma_crossover",
    label: "MA Crossover",
    symbol: SYMBOL,
    isActive: true,
    description: "5/15 SMA trend-following crossover — driving this demo",
    colorVar: "--series-blue",
  },
  {
    id: "rsi_mean_reversion",
    label: "RSI Mean Reversion",
    symbol: SYMBOL,
    isActive: false,
    description: "Buys oversold (RSI<30), sells overbought (RSI>70)",
    colorVar: "--series-aqua",
  },
  {
    id: "bollinger_bands",
    label: "Bollinger Bands",
    symbol: SYMBOL,
    isActive: false,
    description: "Buys below the lower band, sells above the upper band",
    colorVar: "--series-yellow",
  },
];

function randomNormal(): number {
  let u = 0;
  let v = 0;
  while (u === 0) u = Math.random();
  while (v === 0) v = Math.random();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

// Candles per trend regime, before the drift direction flips. Keeps the walk
// from being pure noise (which crosses an SMA pair only by luck) — real
// price series trend and reverse, and this demo needs to too so a visitor
// reliably sees a signal within a minute or so of watching.
function randomRegimeLength(): number {
  return 6 + Math.floor(Math.random() * 8);
}

function sma(values: number[], period: number): number | null {
  if (values.length < period) return null;
  let total = 0;
  for (let i = values.length - period; i < values.length; i++) total += values[i];
  return total / period;
}

let idCounter = 0;
function nextId(prefix: string): string {
  idCounter += 1;
  return `${prefix}-${idCounter}`;
}

export class MockMarketEngine {
  private candles: Candle[] = [];
  private closes: number[] = [];
  private cash = STARTING_CASH;
  private position: Position | null = null;
  private trades: Trade[] = [];
  private signals: Signal[] = [];
  private equityCurve: EquityPoint[] = [];
  private secondsIntoCandle = 0;
  private lastPrice = STARTING_PRICE;
  private driftDirection: 1 | -1 = Math.random() < 0.5 ? 1 : -1;
  private candlesUntilFlip = randomRegimeLength();
  // Rebuilt only when state actually changes (in tick()), so repeated
  // snapshot() calls between ticks return the same reference — required by
  // useSyncExternalStore, which otherwise assumes a new object means the
  // store changed and re-renders in a loop.
  private cached!: MarketSnapshot;

  constructor() {
    this.seedHistory();
    this.cached = this.buildSnapshot();
  }

  private seedHistory(count = 180) {
    const now = Math.floor(Date.now() / 1000);
    let price = STARTING_PRICE;
    for (let i = count; i > 0; i--) {
      const time = now - i * SECONDS_PER_CANDLE;
      const open = price;
      price = Math.max(1, price * (1 + 0.0009 * this.driftDirection + randomNormal() * 0.005));
      this.advanceRegime();
      const close = price;
      const high = Math.max(open, close) * (1 + Math.random() * 0.0015);
      const low = Math.min(open, close) * (1 - Math.random() * 0.0015);
      this.candles.push({ time, open, high, low, close, volume: 5 + Math.random() * 15 });
      this.closes.push(close);
    }
    this.lastPrice = price;
    this.equityCurve.push({ time: now, equity: this.equity() });
  }

  private equity(): number {
    if (!this.position) return this.cash;
    return this.cash + this.position.qty * this.lastPrice;
  }

  private advanceRegime() {
    this.candlesUntilFlip -= 1;
    if (this.candlesUntilFlip <= 0) {
      this.driftDirection = this.driftDirection === 1 ? -1 : 1;
      this.candlesUntilFlip = randomRegimeLength();
    }
  }

  private applyPriceTick() {
    const perTickDrift = (0.0009 * this.driftDirection) / SECONDS_PER_CANDLE;
    this.lastPrice = Math.max(1, this.lastPrice * (1 + perTickDrift + randomNormal() * 0.002));
    const current = this.candles[this.candles.length - 1];
    current.close = this.lastPrice;
    current.high = Math.max(current.high, this.lastPrice);
    current.low = Math.min(current.low, this.lastPrice);
    current.volume += Math.random() * 0.5;

    if (this.position) {
      this.position.currentPrice = this.lastPrice;
      this.position.unrealizedPnl = (this.lastPrice - this.position.avgEntryPrice) * this.position.qty;
      this.position.unrealizedPnlPct = (this.lastPrice / this.position.avgEntryPrice - 1) * 100;
    }
  }

  private finalizeCandle() {
    this.closes.push(this.lastPrice);
    if (this.closes.length > MAX_CANDLES * 2) this.closes.shift();

    const now = Math.floor(Date.now() / 1000);
    this.candles.push({
      time: now,
      open: this.lastPrice,
      high: this.lastPrice,
      low: this.lastPrice,
      close: this.lastPrice,
      volume: 0,
    });
    if (this.candles.length > MAX_CANDLES) this.candles.shift();

    this.advanceRegime();
    this.evaluateStrategy(now);

    this.equityCurve.push({ time: now, equity: this.equity() });
    if (this.equityCurve.length > MAX_EQUITY_POINTS) this.equityCurve.shift();
  }

  private evaluateStrategy(timeSec: number) {
    const fast = sma(this.closes, FAST_PERIOD);
    const slow = sma(this.closes, SLOW_PERIOD);
    const prevFast = sma(this.closes.slice(0, -1), FAST_PERIOD);
    const prevSlow = sma(this.closes.slice(0, -1), SLOW_PERIOD);
    if (fast === null || slow === null || prevFast === null || prevSlow === null) return;

    const crossedUp = prevFast <= prevSlow && fast > slow;
    const crossedDown = prevFast >= prevSlow && fast < slow;
    if (!crossedUp && !crossedDown) return;

    const spread = Math.abs(fast - slow) / this.lastPrice;
    const confidence = Math.min(1, spread * 20 + 0.3);
    const signal: Signal = {
      id: nextId("sig"),
      action: crossedUp ? "BUY" : "SELL",
      confidence,
      symbol: SYMBOL,
      timestamp: timeSec * 1000,
      strategyName: "ma_crossover",
    };
    this.signals.unshift(signal);
    if (this.signals.length > MAX_FEED_ITEMS) this.signals.pop();

    this.maybeExecute(signal, timeSec);
  }

  private maybeExecute(signal: Signal, timeSec: number) {
    const slippage = signal.action === "BUY" ? 1.0005 : 0.9995;
    const fillPrice = this.lastPrice * slippage;

    if (signal.action === "BUY") {
      if (this.position) return; // one lot at a time, mirrors RiskManager.evaluate
      const allocation = Math.min(this.equity() * 0.1 * signal.confidence, this.cash);
      const qty = allocation / fillPrice;
      if (qty <= 0) return;
      const fee = allocation * 0.001;
      this.cash -= allocation + fee;
      this.position = {
        symbol: SYMBOL,
        qty,
        avgEntryPrice: fillPrice,
        currentPrice: this.lastPrice,
        unrealizedPnl: 0,
        unrealizedPnlPct: 0,
      };
      this.recordTrade(signal, "BUY", qty, fillPrice, fee, timeSec);
    } else if (signal.action === "SELL" && this.position) {
      const qty = this.position.qty;
      const notional = qty * fillPrice;
      const fee = notional * 0.001;
      this.cash += notional - fee;
      this.recordTrade(signal, "SELL", qty, fillPrice, fee, timeSec);
      this.position = null;
    }
  }

  private recordTrade(
    signal: Signal,
    side: "BUY" | "SELL",
    qty: number,
    price: number,
    fee: number,
    timeSec: number,
  ) {
    this.trades.unshift({
      id: nextId("trade"),
      symbol: signal.symbol,
      side,
      qty,
      price,
      fee,
      timestamp: timeSec * 1000,
      strategyName: signal.strategyName,
      confidence: signal.confidence,
    });
    if (this.trades.length > MAX_FEED_ITEMS) this.trades.pop();
  }

  tick(): void {
    this.secondsIntoCandle += 1;
    this.applyPriceTick();
    if (this.secondsIntoCandle >= SECONDS_PER_CANDLE) {
      this.secondsIntoCandle = 0;
      this.finalizeCandle();
    }
    this.cached = this.buildSnapshot();
  }

  snapshot(): MarketSnapshot {
    return this.cached;
  }

  private buildSnapshot(): MarketSnapshot {
    return {
      symbol: SYMBOL,
      candles: [...this.candles],
      portfolio: {
        cash: this.cash,
        startingCash: STARTING_CASH,
        equity: this.equity(),
        positions: this.position ? [{ ...this.position }] : [],
      },
      equityCurve: [...this.equityCurve],
      trades: [...this.trades],
      signals: [...this.signals],
      strategies: STRATEGIES,
    };
  }
}
