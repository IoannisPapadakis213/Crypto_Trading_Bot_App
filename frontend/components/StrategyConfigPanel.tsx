"use client";

import { useState } from "react";
import { Card } from "./ui/Card";
import type { StrategyConfig } from "@/lib/types";

function Switch({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={`relative h-5 w-9 shrink-0 rounded-full transition-colors ${
        checked ? "bg-[var(--status-good)]" : "bg-white/15"
      }`}
    >
      <span
        className={`absolute top-0.5 h-4 w-4 rounded-full bg-white transition-transform ${
          checked ? "translate-x-4" : "translate-x-0.5"
        }`}
      />
    </button>
  );
}

export function StrategyConfigPanel({ strategies }: { strategies: StrategyConfig[] }) {
  const [active, setActive] = useState<Record<string, boolean>>(
    Object.fromEntries(strategies.map((s) => [s.id, s.isActive])),
  );

  return (
    <Card title="Strategies">
      <ul className="divide-y divide-white/10">
        {strategies.map((strategy) => (
          <li key={strategy.id} className="flex items-start justify-between gap-3 p-4">
            <div className="flex items-start gap-2.5">
              <span
                className="mt-1.5 h-2 w-2 shrink-0 rounded-full"
                style={{ backgroundColor: `var(${strategy.colorVar})` }}
              />
              <div>
                <p className="text-sm font-medium text-[var(--text-primary)]">{strategy.label}</p>
                <p className="text-xs text-[var(--text-muted)]">{strategy.description}</p>
              </div>
            </div>
            <Switch
              checked={active[strategy.id]}
              onChange={(v) => setActive((prev) => ({ ...prev, [strategy.id]: v }))}
            />
          </li>
        ))}
      </ul>
    </Card>
  );
}
