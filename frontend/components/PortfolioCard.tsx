import { Card } from "./ui/Card";
import { formatCurrency, formatPct, formatQty } from "@/lib/format";
import type { Portfolio } from "@/lib/types";

export function PortfolioCard({ portfolio }: { portfolio: Portfolio }) {
  const totalReturn = portfolio.equity - portfolio.startingCash;
  const totalReturnPct = (totalReturn / portfolio.startingCash) * 100;
  const isUp = totalReturn >= 0;

  return (
    <Card title="Portfolio">
      <div className="space-y-4 p-4">
        <div>
          <p className="text-xs text-[var(--text-muted)]">Equity</p>
          <p className="tabular-nums text-2xl font-semibold text-[var(--text-primary)]">
            {formatCurrency(portfolio.equity)}
          </p>
          <p
            className={`tabular-nums text-sm font-medium ${
              isUp ? "text-[var(--status-good)]" : "text-[var(--status-critical)]"
            }`}
          >
            {formatPct(totalReturnPct, { signed: true })} ({formatCurrency(totalReturn)})
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3 border-t border-white/10 pt-3">
          <div>
            <p className="text-xs text-[var(--text-muted)]">Cash</p>
            <p className="tabular-nums text-sm text-[var(--text-secondary)]">
              {formatCurrency(portfolio.cash)}
            </p>
          </div>
          <div>
            <p className="text-xs text-[var(--text-muted)]">Starting capital</p>
            <p className="tabular-nums text-sm text-[var(--text-secondary)]">
              {formatCurrency(portfolio.startingCash)}
            </p>
          </div>
        </div>

        <div className="border-t border-white/10 pt-3">
          <p className="mb-2 text-xs text-[var(--text-muted)]">Open positions</p>
          {portfolio.positions.length === 0 ? (
            <p className="text-sm text-[var(--text-muted)]">No open positions</p>
          ) : (
            <ul className="space-y-2">
              {portfolio.positions.map((pos) => {
                const posUp = pos.unrealizedPnl >= 0;
                return (
                  <li
                    key={pos.symbol}
                    className="flex items-center justify-between rounded-lg bg-white/5 px-3 py-2"
                  >
                    <div>
                      <p className="text-sm font-medium text-[var(--text-primary)]">{pos.symbol}</p>
                      <p className="tabular-nums text-xs text-[var(--text-muted)]">
                        {formatQty(pos.qty)} @ {formatCurrency(pos.avgEntryPrice)}
                      </p>
                    </div>
                    <p
                      className={`tabular-nums text-sm font-medium ${
                        posUp ? "text-[var(--status-good)]" : "text-[var(--status-critical)]"
                      }`}
                    >
                      {formatPct(pos.unrealizedPnlPct, { signed: true })}
                    </p>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </div>
    </Card>
  );
}
