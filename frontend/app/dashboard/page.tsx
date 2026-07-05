"use client";

import { useMockMarket } from "@/lib/use-mock-market";
import { CandlestickChart } from "@/components/CandlestickChart";
import { EquityCurve } from "@/components/EquityCurve";
import { PortfolioCard } from "@/components/PortfolioCard";
import { SignalFeed } from "@/components/SignalFeed";
import { StrategyConfigPanel } from "@/components/StrategyConfigPanel";
import { Card } from "@/components/ui/Card";
import { formatCurrency, formatPct } from "@/lib/format";

export default function DashboardPage() {
  const snapshot = useMockMarket();

  if (!snapshot) {
    return (
      <div className="flex h-screen items-center justify-center bg-[var(--page-plane)]">
        <p className="text-sm text-[var(--text-muted)]">Booting paper trading engine&hellip;</p>
      </div>
    );
  }

  const { symbol, candles, portfolio, equityCurve, signals, strategies } = snapshot;

  const lastPrice = candles.at(-1)?.close ?? 0;
  const firstPrice = candles[0]?.close ?? lastPrice;
  const priceChangePct = firstPrice ? ((lastPrice - firstPrice) / firstPrice) * 100 : 0;
  const priceUp = priceChangePct >= 0;

  return (
    <div className="flex h-screen flex-col bg-[var(--page-plane)]">
      <header className="flex shrink-0 items-center justify-between border-b border-white/10 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--series-blue)] text-sm font-bold text-white">
            AI
          </div>
          <div>
            <h1 className="text-sm font-semibold text-[var(--text-primary)]">AI Trader</h1>
            <p className="text-xs text-[var(--text-muted)]">Paper trading &middot; not financial advice</p>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="text-right">
            <p className="text-xs text-[var(--text-muted)]">{symbol}</p>
            <p className="tabular-nums text-lg font-semibold text-[var(--text-primary)]">
              {formatCurrency(lastPrice)}
            </p>
          </div>
          <div
            className={`tabular-nums rounded-md px-2 py-1 text-sm font-medium ${
              priceUp
                ? "bg-[var(--status-good)]/15 text-[var(--status-good)]"
                : "bg-[var(--status-critical)]/15 text-[var(--status-critical)]"
            }`}
          >
            {formatPct(priceChangePct, { signed: true })}
          </div>
        </div>
      </header>

      <main className="grid min-h-0 flex-1 grid-cols-1 gap-4 overflow-hidden p-4 lg:grid-cols-3">
        <div className="flex min-h-0 flex-col gap-4 lg:col-span-2">
          <Card className="min-h-0 flex-[3]">
            <CandlestickChart candles={candles} symbol={symbol} />
          </Card>
          <Card title="Equity Curve" className="min-h-0 flex-[2]">
            <div className="h-full min-h-0 p-2">
              <EquityCurve equityCurve={equityCurve} startingCash={portfolio.startingCash} />
            </div>
          </Card>
        </div>

        <div className="flex min-h-0 flex-col gap-4 overflow-y-auto lg:overflow-visible">
          <PortfolioCard portfolio={portfolio} />
          <StrategyConfigPanel strategies={strategies} />
          <SignalFeed signals={signals} />
        </div>
      </main>
    </div>
  );
}
