"""
SP2L — Spike + Two-Leg pullback (مفهوم عمومی).

رأی مستقل؛ تصمیم نهایی فقط از Ensemble.
"""
from __future__ import annotations

from exchange.adapters.base import OHLCV
from scanner.ensemble_engine import StrategyVote
from scanner.indicators import atr as _scanner_atr, Candle as _C


def vote_sp2l(candles: list[OHLCV], lookback: int = 20) -> StrategyVote:
    if len(candles) < lookback + 8:
        return StrategyVote("SP2L", "NEUTRAL", 40, "داده کافی برای SP2L نیست.", 0.8)

    sc = [_C(c.timestamp, c.open, c.high, c.low, c.close, c.volume) for c in candles]
    a = _scanner_atr(sc)
    if not a or a <= 0:
        return StrategyVote("SP2L", "NEUTRAL", 40, "ATR نامعتبر برای SP2L.", 0.7)

    last = candles[-1]
    body = abs(last.close - last.open)
    ranges = [c.high - c.low for c in candles[-lookback - 1 : -1]]
    avg_range = sum(ranges) / len(ranges) if ranges else a
    spike = body >= max(a * 1.15, avg_range * 1.4)

    changes = [candles[i].close - candles[i - 1].close for i in range(len(candles) - 6, len(candles))]
    signs = [1 if x > 0 else -1 if x < 0 else 0 for x in changes]
    transitions = sum(1 for i in range(1, len(signs)) if signs[i] and signs[i] != signs[i - 1])
    two_leg = transitions >= 2

    if spike and two_leg:
        direction = "BUY" if last.close > last.open else "SELL"
        return StrategyVote(
            "SP2L",
            direction,
            82,
            "اسپایک همراه با ساختار اصلاح چندلگی (مفهوم عمومی SP2L).",
            1.0,
        )
    if spike:
        direction = "BUY" if last.close > last.open else "SELL"
        return StrategyVote(
            "SP2L",
            direction,
            68,
            "اسپایک شناسایی شد؛ ساختار دو لگ کامل نیست.",
            0.85,
        )
    return StrategyVote("SP2L", "NEUTRAL", 45, "شرایط SP2L برقرار نیست.", 0.8)
