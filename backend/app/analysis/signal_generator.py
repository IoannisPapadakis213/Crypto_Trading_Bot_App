"""Ensemble logic: combine the 5 indicator opinions into one action with a
confidence score.

Rule: the plurality label among BUY/SELL/NEUTRAL wins. A plurality tie falls
back to NEUTRAL (conservative default) which always maps to a final HOLD.
"""

from collections import Counter
from datetime import UTC, datetime

from app.analysis.indicators import IndicatorResult
from app.schemas.signals import IndicatorBreakdownOut, SignalOut


def build_ensemble_signal(symbol: str, indicator_results: list[IndicatorResult]) -> SignalOut:
    counts = Counter(r.signal for r in indicator_results)
    max_count = max(counts.values())
    leaders = [label for label, count in counts.items() if count == max_count]

    winning_label = leaders[0] if len(leaders) == 1 else "NEUTRAL"
    final_signal = "HOLD" if winning_label == "NEUTRAL" else winning_label

    # Deliberately NOT `max_count`: when BUY/SELL tie and NEUTRAL isn't the
    # plurality (e.g. 2 BUY / 2 SELL / 1 NEUTRAL), the tie-break above still
    # picks HOLD, but confidence should reflect the actual NEUTRAL count
    # (low, "indicators disagree") rather than the tied BUY/SELL count —
    # that's a different situation from a genuine 5/5 NEUTRAL HOLD.
    agreeing = counts.get(winning_label, 0)
    confidence = agreeing / len(indicator_results)

    return SignalOut(
        symbol=symbol,
        final_signal=final_signal,
        confidence=round(confidence, 4),
        timestamp=datetime.now(UTC),
        breakdown=[
            IndicatorBreakdownOut(indicator=r.name, signal=r.signal, values=r.values)
            for r in indicator_results
        ],
    )
