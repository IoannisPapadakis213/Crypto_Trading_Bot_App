import { ArrowDown, ArrowUp, Minus } from "lucide-react";
import type { SignalAction } from "@/lib/types";

const STYLES: Record<SignalAction, { bg: string; fg: string; Icon: typeof ArrowUp; label: string }> = {
  BUY: { bg: "bg-[var(--status-good)]/15", fg: "text-[var(--status-good)]", Icon: ArrowUp, label: "BUY" },
  SELL: { bg: "bg-[var(--status-critical)]/15", fg: "text-[var(--status-critical)]", Icon: ArrowDown, label: "SELL" },
  HOLD: { bg: "bg-white/5", fg: "text-[var(--text-muted)]", Icon: Minus, label: "HOLD" },
};

export function ActionBadge({ action }: { action: SignalAction }) {
  const { bg, fg, Icon, label } = STYLES[action];
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-xs font-semibold ${bg} ${fg}`}
    >
      <Icon size={12} strokeWidth={2.5} />
      {label}
    </span>
  );
}
