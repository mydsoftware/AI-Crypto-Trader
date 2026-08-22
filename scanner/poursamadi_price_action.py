"""الگوهای قابل‌محاسبه از رویکرد عمومی پورصمدی.

این پیاده‌سازی از توضیحات عمومی منتشرشده درباره چرخه Spike، SP2L، Pro BTB و
MicroMAP استفاده می‌کند و ادعا نمی‌کند قوانین آموزشی خصوصی یا جزئیات کامل دوره را بازسازی کرده است.
هدف، تبدیل مفاهیم عمومی به یک رأی مستقل برای موتور اجماع است.
"""
from __future__ import annotations

from dataclasses import dataclass
from .indicators import Candle, atr, ema
from .ensemble_engine import StrategyVote


@dataclass(slots=True)
class PriceActionState:
    spike: bool
    channel: bool
    range_market: bool
    breakout_retest: bool
    two_leg_pullback: bool
    micro_channel: bool
    level: float | None


def detect_state(candles: list[Candle], lookback: int = 20) -> PriceActionState:
    if len(candles) < max(lookback + 5, 30):
        return PriceActionState(False, False, False, False, False, False, None)

    recent = candles[-lookback:]
    a = atr(candles, 14)
    if not a or a <= 0:
        return PriceActionState(False, False, False, False, False, False, None)

    last = candles[-1]
    body = abs(last.close - last.open)
    ranges = [c.high - c.low for c in candles[-lookback-1:-1]]
    avg_range = sum(ranges) / len(ranges) if ranges else a
    spike = body >= max(a * 1.2, avg_range * 1.5)

    highs = [c.high for c in recent]
    lows = [c.low for c in recent]
    width = max(highs) - min(lows)
    channel = width >= a * 2.0 and not spike
    range_market = width <= a * 4.0 and not spike

    breakout_level = max(c.high for c in candles[-lookback-1:-1])
    breakdown_level = min(c.low for c in candles[-lookback-1:-1])
    breakout_retest = (
        last.low <= breakout_level <= last.high
        and last.close > breakout_level
    ) or (
        last.low <= breakdown_level <= last.high
        and last.close < breakdown_level
    )

    # دو لگ: دو موج اصلاحی ساده با تغییر جهت‌های متوالی در پنجره اخیر.
    changes = [candles[i].close - candles[i-1].close for i in range(len(candles)-6, len(candles))]
    signs = [1 if x > 0 else -1 if x < 0 else 0 for x in changes]
    transitions = sum(1 for i in range(1, len(signs)) if signs[i] and signs[i] != signs[i-1])
    two_leg_pullback = transitions >= 2 and not spike

    closes = [c.close for c in candles]
    e9, e21 = ema(closes, 9), ema(closes, 21)
    micro_channel = bool(e9 and e21 and abs(e9 - e21) <= a * 0.35)

    return PriceActionState(spike, channel, range_market, breakout_retest, two_leg_pullback, micro_channel, breakout_level if last.close >= breakout_level else breakdown_level)


def generate_poursamadi_votes(candles: list[Candle]) -> list[StrategyVote]:
    """رأی مستقل از مفاهیم عمومی این سبک؛ نتیجه باید در اجماع کل سیستم تأیید شود."""
    state = detect_state(candles)
    if not candles:
        return []
    last = candles[-1]
    votes: list[StrategyVote] = []

    if state.spike:
        direction = "BUY" if last.close > last.open else "SELL"
        votes.append(StrategyVote("Poursamadi Spike Cycle", direction, 78, "حرکت شارپ/اسپایک نسبت به دامنه معمول بازار شناسایی شد.", 1.0))

    if state.breakout_retest:
        direction = "BUY" if last.close > last.open else "SELL"
        votes.append(StrategyVote("Pro BTB", direction, 84, "شکست سطح و بازگشت/تست مجدد سطح شکست شناسایی شد.", 1.05))

    if state.two_leg_pullback and state.spike:
        direction = "BUY" if last.close > last.open else "SELL"
        votes.append(StrategyVote("SP2L", direction, 82, "اسپایک همراه با ساختار اصلاح چندلگی شناسایی شد.", 1.0))

    if state.micro_channel:
        direction = "BUY" if last.close > last.open else "SELL"
        votes.append(StrategyVote("MicroMAP", direction, 74, "میکروکانال فشرده و احتمال پایان پولبک کوتاه شناسایی شد.", 0.9))

    if state.range_market:
        votes.append(StrategyVote("Spike Cycle Regime", "NEUTRAL", 58, "بازار در فاز رنج/بدون اسپایک واضح است؛ ورود اجباراً تولید نمی‌شود.", 1.0))

    return votes
