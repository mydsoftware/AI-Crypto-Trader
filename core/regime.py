"""
تشخیص رژیم بازار.

رژیمها:
- Bull / Bear / Sideways
- Trending / Ranging
- High Volatility / Low Volatility
- Accumulation / Distribution (تقریبی)

وزن استراتژی‌ها می‌تواند بر اساس رژیم تغییر کند.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from exchange.adapters.base import OHLCV
from core.technical import adx, atr, ema, sma


@dataclass(slots=True)
class MarketRegime:
    primary: str
    structure: str
    volatility: str
    phase: str
    confidence: float
    reasons: list[str]
    strategy_weights: dict[str, float]


def detect_regime(candles: Sequence[OHLCV]) -> MarketRegime:
    reasons: list[str] = []
    if len(candles) < 60:
        return MarketRegime(
            "Sideways", "Ranging", "Normal", "Neutral", 20,
            ["داده کافی برای تشخیص رژیم نیست."],
            {"trend": 0.5, "breakout": 0.5, "mean_reversion": 0.5, "momentum": 0.5},
        )

    closes = [c.close for c in candles]
    price = closes[-1]
    e21 = ema(closes, 21)
    e50 = ema(closes, 50)
    s50 = sma(closes, 50)
    s200 = sma(closes, 200) if len(closes) >= 200 else None
    a = atr(list(candles))
    adx_val = adx(list(candles))

    primary = "Sideways"
    if e21 and e50 and s50:
        if price > e21 > e50 and (s200 is None or s50 > s200):
            primary = "Bull"
            reasons.append("ساختار قیمت بالای EMAها و هم‌جهت صعودی.")
        elif price < e21 < e50 and (s200 is None or s50 < s200):
            primary = "Bear"
            reasons.append("ساختار قیمت زیر EMAها و هم‌جهت نزولی.")
        else:
            reasons.append("روند غالب واضح نیست.")

    structure = "Ranging"
    if adx_val is not None and adx_val >= 25:
        structure = "Trending"
        reasons.append(f"ADX≈{adx_val:.0f} — بازار رونددار.")
    else:
        reasons.append(f"ADX≈{adx_val:.0f} — بازار رنج‌مانند." if adx_val else "ADX ناموجود.")

    volatility = "Normal"
    if a and price > 0:
        vol_pct = a / price * 100
        if vol_pct >= 1.5:
            volatility = "High"
            reasons.append(f"نوسان بالا (ATR≈{vol_pct:.2f}%).")
        elif vol_pct <= 0.5:
            volatility = "Low"
            reasons.append(f"نوسان پایین (ATR≈{vol_pct:.2f}%).")
        else:
            reasons.append(f"نوسان متعادل (ATR≈{vol_pct:.2f}%).")

    phase = "Neutral"
    if len(closes) >= 30:
        recent = closes[-15:]
        older = closes[-30:-15]
        recent_vol = sum(abs(recent[i] - recent[i - 1]) for i in range(1, len(recent)))
        older_vol = sum(abs(older[i] - older[i - 1]) for i in range(1, len(older)))
        if primary == "Sideways" and recent_vol < older_vol * 0.85:
            phase = "Accumulation"
            reasons.append("کاهش نوسان در رنج — احتمال انباشت.")
        elif primary == "Bull" and volatility == "High":
            phase = "Distribution"
            reasons.append("روند صعودی + نوسان بالا — احتیاط توزیع.")

    conf = 50.0
    if structure == "Trending":
        conf += 15
    if primary in ("Bull", "Bear"):
        conf += 15
    if adx_val and adx_val >= 30:
        conf += 10
    conf = min(95.0, conf)

    weights = {
        "trend": 1.0,
        "breakout": 1.0,
        "mean_reversion": 1.0,
        "momentum": 1.0,
        "poursamadi": 1.0,
    }
    if structure == "Trending" and primary == "Bull":
        weights.update({"trend": 1.25, "momentum": 1.15, "breakout": 1.1, "mean_reversion": 0.6})
    elif structure == "Trending" and primary == "Bear":
        weights.update({"trend": 1.2, "momentum": 1.1, "breakout": 1.05, "mean_reversion": 0.55})
    elif structure == "Ranging":
        weights.update({"mean_reversion": 1.25, "trend": 0.65, "breakout": 0.85, "momentum": 0.7})
    if volatility == "High":
        weights["breakout"] = weights.get("breakout", 1.0) * 1.1
        weights["poursamadi"] = 1.15
    if volatility == "Low":
        weights["mean_reversion"] = weights.get("mean_reversion", 1.0) * 1.1

    return MarketRegime(
        primary=primary,
        structure=structure,
        volatility=volatility,
        phase=phase,
        confidence=round(conf, 1),
        reasons=reasons,
        strategy_weights=weights,
    )
