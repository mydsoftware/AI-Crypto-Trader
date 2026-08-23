"""
MicroMAP — میکروکانال / پولبک فشرده (مفهوم عمومی).

رأی مستقل؛ تصمیم نهایی فقط از Ensemble.
"""
from __future__ import annotations

from exchange.adapters.base import OHLCV
from scanner.ensemble_engine import StrategyVote
from scanner.indicators import atr as _scanner_atr, ema, Candle as _C


def vote_micromap(candles: list[OHLCV]) -> StrategyVote:
    if len(candles) < 30:
        return StrategyVote("MicroMAP", "NEUTRAL", 40, "داده کافی برای MicroMAP نیست.", 0.8)

    closes = [c.close for c in candles]
    sc = [_C(c.timestamp, c.open, c.high, c.low, c.close, c.volume) for c in candles]
    a = _scanner_atr(sc)
    e9 = ema(closes, 9)
    e21 = ema(closes, 21)
    if not a or e9 is None or e21 is None:
        return StrategyVote("MicroMAP", "NEUTRAL", 40, "اندیکاتورهای MicroMAP ناقص است.", 0.7)

    micro = abs(e9 - e21) <= a * 0.4
    last = candles[-1]
    price = last.close

    if micro and price > e9 > e21:
        return StrategyVote(
            "MicroMAP",
            "BUY",
            74,
            "میکروکانال فشرده صعودی — احتمال پایان پولبک کوتاه (مفهوم عمومی).",
            0.9,
        )
    if micro and price < e9 < e21:
        return StrategyVote(
            "MicroMAP",
            "SELL",
            74,
            "میکروکانال فشرده نزولی — احتمال ادامه فشار فروش (مفهوم عمومی).",
            0.9,
        )
    if micro:
        return StrategyVote(
            "MicroMAP",
            "NEUTRAL",
            55,
            "میکروکانال فشرده بدون جهت واضح.",
            0.85,
        )
    return StrategyVote("MicroMAP", "NEUTRAL", 42, "میکروکانال فشرده شناسایی نشد.", 0.75)
