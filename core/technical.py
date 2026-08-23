"""
موتور تکنیکال — اندیکاتورها + تولید Evidence.

هر اندیکاتور فقط عدد تولید نمی‌کند؛ Evidence جهت‌دار با دلیل می‌سازد.
بدون تضمین سود.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Sequence

from exchange.adapters.base import OHLCV


@dataclass(slots=True)
class Evidence:
    """شواهد تحلیلی یک اندیکاتور یا قانون."""
    name: str
    direction: str  # BUY / SELL / NEUTRAL
    score: float  # 0-100
    reason: str
    weight: float = 1.0


def _closes(candles: Sequence[OHLCV]) -> list[float]:
    return [c.close for c in candles]


def sma(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def ema(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    value = sum(values[:period]) / period
    mult = 2 / (period + 1)
    for price in values[period:]:
        value = (price - value) * mult + value
    return value


def rsi(values: list[float], period: int = 14) -> float | None:
    if len(values) < period + 1:
        return None
    changes = [values[i] - values[i - 1] for i in range(1, len(values))]
    gains = [max(x, 0.0) for x in changes[-period:]]
    losses = [max(-x, 0.0) for x in changes[-period:]]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    return 100 - (100 / (1 + avg_gain / avg_loss))


def atr(candles: Sequence[OHLCV], period: int = 14) -> float | None:
    if len(candles) < period + 1:
        return None
    trs: list[float] = []
    for i in range(1, len(candles)):
        c, p = candles[i], candles[i - 1]
        trs.append(max(c.high - c.low, abs(c.high - p.close), abs(c.low - p.close)))
    return sum(trs[-period:]) / period


def bollinger(values: list[float], period: int = 20, deviations: float = 2.0) -> tuple[float, float, float] | None:
    if len(values) < period:
        return None
    window = values[-period:]
    middle = sum(window) / period
    variance = sum((x - middle) ** 2 for x in window) / period
    sd = sqrt(variance)
    return middle - deviations * sd, middle, middle + deviations * sd


def macd(values: list[float], fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[float, float, float] | None:
    if len(values) < slow + signal:
        return None
    ema_fast = ema(values, fast)
    ema_slow = ema(values, slow)
    if ema_fast is None or ema_slow is None:
        return None
    macd_line = ema_fast - ema_slow
    macd_series: list[float] = []
    ef = sum(values[:fast]) / fast
    es = sum(values[:slow]) / slow
    mf, ms = 2 / (fast + 1), 2 / (slow + 1)
    for i, price in enumerate(values):
        if i >= fast:
            ef = (price - ef) * mf + ef
        if i >= slow:
            es = (price - es) * ms + es
            macd_series.append(ef - es)
    if len(macd_series) < signal:
        return macd_line, macd_line, 0.0
    sig = ema(macd_series, signal)
    if sig is None:
        return macd_line, macd_line, 0.0
    return macd_line, sig, macd_line - sig


def stochastic(candles: Sequence[OHLCV], k_period: int = 14, d_period: int = 3) -> tuple[float, float] | None:
    if len(candles) < k_period + d_period:
        return None
    k_values: list[float] = []
    for i in range(k_period - 1, len(candles)):
        window = candles[i - k_period + 1 : i + 1]
        highest = max(c.high for c in window)
        lowest = min(c.low for c in window)
        if highest == lowest:
            k_values.append(50.0)
        else:
            k_values.append((candles[i].close - lowest) / (highest - lowest) * 100)
    if len(k_values) < d_period:
        return None
    k = k_values[-1]
    d = sum(k_values[-d_period:]) / d_period
    return k, d


def adx(candles: Sequence[OHLCV], period: int = 14) -> float | None:
    if len(candles) < period * 2:
        return None
    plus_dm: list[float] = []
    minus_dm: list[float] = []
    trs: list[float] = []
    for i in range(1, len(candles)):
        up = candles[i].high - candles[i - 1].high
        down = candles[i - 1].low - candles[i].low
        plus_dm.append(up if up > down and up > 0 else 0.0)
        minus_dm.append(down if down > up and down > 0 else 0.0)
        c, p = candles[i], candles[i - 1]
        trs.append(max(c.high - c.low, abs(c.high - p.close), abs(c.low - p.close)))
    if len(trs) < period:
        return None
    atr_val = sum(trs[-period:]) / period
    if atr_val == 0:
        return 0.0
    plus_di = 100 * (sum(plus_dm[-period:]) / period) / atr_val
    minus_di = 100 * (sum(minus_dm[-period:]) / period) / atr_val
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) else 0
    return dx


def volume_ratio(candles: Sequence[OHLCV], period: int = 20) -> float | None:
    if len(candles) < period + 1:
        return None
    avg = sum(c.volume for c in candles[-period - 1 : -1]) / period
    return candles[-1].volume / avg if avg else None


def donchian(candles: Sequence[OHLCV], period: int = 20) -> tuple[float, float] | None:
    if len(candles) < period + 1:
        return None
    window = candles[-period - 1 : -1]
    return max(c.high for c in window), min(c.low for c in window)


def generate_technical_evidence(candles: Sequence[OHLCV]) -> list[Evidence]:
    if len(candles) < 60:
        return [Evidence("DATA", "NEUTRAL", 0, "داده کافی برای تحلیل تکنیکال وجود ندارد.", 0.5)]

    closes = _closes(list(candles))
    price = closes[-1]
    evidences: list[Evidence] = []

    e9, e21 = ema(closes, 9), ema(closes, 21)
    if e9 is not None and e21 is not None:
        if e9 > e21 and price > e9:
            evidences.append(Evidence("EMA Trend", "BUY", 78, "EMA9 بالای EMA21 و قیمت بالای EMA9 است.", 1.0))
        elif e9 < e21 and price < e9:
            evidences.append(Evidence("EMA Trend", "SELL", 78, "EMA9 زیر EMA21 و قیمت زیر EMA9 است.", 1.0))
        else:
            evidences.append(Evidence("EMA Trend", "NEUTRAL", 45, "EMAهای کوتاه‌مدت هم‌جهت واضح نیستند.", 0.8))

    s50 = sma(closes, 50)
    s200 = sma(closes, 200) if len(closes) >= 200 else None
    if s50 is not None and s200 is not None:
        if s50 > s200 and price > s50:
            evidences.append(Evidence("SMA Structure", "BUY", 82, "ساختار SMA50/SMA200 صعودی است.", 1.05))
        elif s50 < s200 and price < s50:
            evidences.append(Evidence("SMA Structure", "SELL", 82, "ساختار SMA50/SMA200 نزولی است.", 1.05))
        else:
            evidences.append(Evidence("SMA Structure", "NEUTRAL", 40, "SMA50/SMA200 اجماع واضح ندارند.", 0.9))

    r = rsi(closes)
    if r is not None:
        if 50 <= r <= 68:
            evidences.append(Evidence("RSI", "BUY", 70, f"RSI در ناحیه مومنتوم صعودی سالم ({r:.1f}).", 0.9))
        elif 32 <= r < 50:
            evidences.append(Evidence("RSI", "SELL", 70, f"RSI در ناحیه مومنتوم نزولی ({r:.1f}).", 0.9))
        elif r > 75:
            evidences.append(Evidence("RSI", "NEUTRAL", 35, f"RSI بیش‌خرید شدید ({r:.1f}) — احتیاط.", 0.7))
        elif r < 25:
            evidences.append(Evidence("RSI", "NEUTRAL", 35, f"RSI بیش‌فروش شدید ({r:.1f}) — احتیاط.", 0.7))
        else:
            evidences.append(Evidence("RSI", "NEUTRAL", 45, f"RSI خنثی ({r:.1f}).", 0.7))

    bb = bollinger(closes)
    if bb:
        low, mid, high = bb
        if price > mid and price < high:
            evidences.append(Evidence("Bollinger", "BUY", 65, "قیمت بالای میانه بولینگر و زیر باند بالا.", 0.85))
        elif price < mid and price > low:
            evidences.append(Evidence("Bollinger", "SELL", 65, "قیمت زیر میانه بولینگر و بالای باند پایین.", 0.85))
        else:
            evidences.append(Evidence("Bollinger", "NEUTRAL", 40, "قیمت در ناحیه افراطی یا خنثی بولینگر.", 0.7))

    m = macd(closes)
    if m:
        line, sig, hist = m
        if hist > 0 and line > sig:
            evidences.append(Evidence("MACD", "BUY", 72, "هیستوگرام MACD مثبت و خط بالای سیگنال.", 1.0))
        elif hist < 0 and line < sig:
            evidences.append(Evidence("MACD", "SELL", 72, "هیستوگرام MACD منفی و خط زیر سیگنال.", 1.0))
        else:
            evidences.append(Evidence("MACD", "NEUTRAL", 42, "MACD اجماع واضحی ندارد.", 0.8))

    st = stochastic(candles)
    if st:
        k, d = st
        if k > d and 20 < k < 80:
            evidences.append(Evidence("Stochastic", "BUY", 68, f"Stochastic صعودی (K={k:.0f}, D={d:.0f}).", 0.85))
        elif k < d and 20 < k < 80:
            evidences.append(Evidence("Stochastic", "SELL", 68, f"Stochastic نزولی (K={k:.0f}, D={d:.0f}).", 0.85))
        else:
            evidences.append(Evidence("Stochastic", "NEUTRAL", 40, f"Stochastic در ناحیه افراطی یا خنثی (K={k:.0f}).", 0.7))

    dc = donchian(candles)
    if dc:
        upper, lower = dc
        if price > upper:
            evidences.append(Evidence("Donchian", "BUY", 88, "شکست سقف کانال دانچیان.", 1.05))
        elif price < lower:
            evidences.append(Evidence("Donchian", "SELL", 88, "شکست کف کانال دانچیان.", 1.05))
        else:
            evidences.append(Evidence("Donchian", "NEUTRAL", 35, "قیمت داخل کانال دانچیان است.", 0.8))

    vr = volume_ratio(candles)
    if vr is not None:
        if vr >= 1.8 and price >= closes[-2]:
            evidences.append(Evidence("Volume", "BUY", 86, f"حجم نسبی {vr:.2f}x همراه با افزایش قیمت.", 1.0))
        elif vr >= 1.8 and price < closes[-2]:
            evidences.append(Evidence("Volume", "SELL", 86, f"حجم نسبی {vr:.2f}x همراه با کاهش قیمت.", 1.0))
        else:
            evidences.append(Evidence("Volume", "NEUTRAL", 40, f"حجم نسبی عادی ({vr:.2f}x).", 0.7))

    a = atr(candles)
    if a and price > 0:
        vol_pct = a / price * 100
        if vol_pct >= 1.2:
            evidences.append(Evidence("Volatility", "NEUTRAL", 55, f"نوسان بالا (ATR≈{vol_pct:.2f}%) — ریسک بیشتر.", 0.8))
        else:
            evidences.append(Evidence("Volatility", "NEUTRAL", 50, f"نوسان متعادل (ATR≈{vol_pct:.2f}%).", 0.6))

    adx_val = adx(candles)
    if adx_val is not None:
        if adx_val >= 25:
            evidences.append(Evidence("ADX", "NEUTRAL", 60, f"روند قوی (ADX≈{adx_val:.0f}) — جهت از سایر شواهد.", 0.9))
        else:
            evidences.append(Evidence("ADX", "NEUTRAL", 40, f"بازار بدون روند قوی (ADX≈{adx_val:.0f}).", 0.7))

    return evidences


def technical_score(evidences: list[Evidence]) -> tuple[float, str]:
    if not evidences:
        return 0.0, "NEUTRAL"
    buy = sum(e.score * e.weight for e in evidences if e.direction == "BUY")
    sell = sum(e.score * e.weight for e in evidences if e.direction == "SELL")
    total = sum(e.score * e.weight for e in evidences)
    if total <= 0:
        return 0.0, "NEUTRAL"
    if buy > sell * 1.15:
        return min(100.0, buy / total * 100), "BUY"
    if sell > buy * 1.15:
        return min(100.0, sell / total * 100), "SELL"
    return 50.0, "NEUTRAL"
