"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Card } from "./ui/Card";
import { ActionBadge } from "./ui/ActionBadge";
import { formatTime } from "@/lib/format";
import type { Signal } from "@/lib/types";

export function SignalFeed({ signals }: { signals: Signal[] }) {
  return (
    <Card title="Signal Feed" className="flex min-h-0 flex-1 flex-col">
      <div className="flex-1 space-y-1 overflow-y-auto p-3">
        {signals.length === 0 ? (
          <p className="p-2 text-sm text-[var(--text-muted)]">
            Waiting for the strategy to see a crossover&hellip;
          </p>
        ) : (
          <AnimatePresence initial={false}>
            {signals.map((signal) => (
              <motion.div
                key={signal.id}
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="flex items-center justify-between gap-3 rounded-lg px-3 py-2 hover:bg-white/5"
              >
                <div className="flex items-center gap-2">
                  <ActionBadge action={signal.action} />
                  <div>
                    <p className="text-sm text-[var(--text-primary)]">{signal.symbol}</p>
                    <p className="text-xs text-[var(--text-muted)]">{signal.strategyName}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="tabular-nums text-xs text-[var(--text-secondary)]">
                    {(signal.confidence * 100).toFixed(0)}% confidence
                  </p>
                  <p className="tabular-nums text-xs text-[var(--text-muted)]">
                    {formatTime(signal.timestamp)}
                  </p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>
    </Card>
  );
}
