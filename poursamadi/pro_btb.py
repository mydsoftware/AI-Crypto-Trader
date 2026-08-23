"""
Pro BTB — Breakout + Retest (مفهوم عمومی).

رأی مستقل؛ تصمیم نهایی فقط از Ensemble.
"""
from __future__ import annotations

from exchange.adapters.base import OHLCV
from scanner.ensemble_engine import StrategyVote


def vote_pro_btb(candles: list[OHLCV], lookback: int = 20) -> StrategyVote:
    if len(candles) < lookback + 5:
        return StrategyVote("Pro BTB", "NEUTRAL", 40, "داده کافی برای Pro BTB نیست.", 0.8)

    window = candles[-lookback - 1 : -1]
    last = candles[-1]
    upper = max(c.high for c in window)
    lower = min(c.low for c in window)

    bullish_btb = (
        last.low <= upper <= last.high
        and last.close > upper
        and last.close > last.open
    )
    bearish_btb = (
        last.low <= lower <= last.high
        and last.close < lower
        and last.close < last.open
    )

    if bullish_btb:
        return StrategyVote(
            "Pro BTB",
            "BUY",
            87,
            "شکست سقف و بازگشت/تست سطح شکست (مفهوم عمومی Pro BTB).",
            1.05,
        )
    if bearish_btb:
        return StrategyVote(
            "Pro BTB",
            "SELL",
            87,
            "شکست کف و بازگشت/تست سطح شکست (مفهوم عمومی Pro BTB).",
            1.05,
        )
    return StrategyVote("Pro BTB", "NEUTRAL", 48, "شکست + تست معتبر تأیید نشده است.", 0.9)
