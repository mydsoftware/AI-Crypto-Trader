"""تولید رأی چند استراتژی از OHLCV."""
from __future__ import annotations
from .indicators import Candle, atr, bollinger, donchian, ema, rsi, sma, volume_ratio
from .ensemble_engine import StrategyVote


def _vote(name: str, direction: str, score: float, reason: str, reliability: float = 1.0) -> StrategyVote:
    return StrategyVote(name, direction, max(0.0, min(100.0, score)), reason, reliability)


def generate_votes(candles: list[Candle]) -> list[StrategyVote]:
    if len(candles) < 60:
        return [_vote("DATA", "NEUTRAL", 0, "برای تحلیل حداقل داده بیشتری لازم است.")]
    closes = [c.close for c in candles]
    price = closes[-1]
    e9, e21, e50 = ema(closes, 9), ema(closes, 21), ema(closes, 50)
    s50, s200 = sma(closes, 50), sma(closes, 200)
    r = rsi(closes)
    bb = bollinger(closes)
    dc = donchian(candles)
    vr = volume_ratio(candles)
    a = atr(candles)
    votes: list[StrategyVote] = []

    if e9 and e21:
        d = "BUY" if e9 > e21 and price > e9 else "SELL" if e9 < e21 and price < e9 else "NEUTRAL"
        votes.append(_vote("EMA Trend", d, 78 if d != "NEUTRAL" else 45, "EMA9 و EMA21 روند کوتاه‌مدت را تأیید می‌کنند." if d != "NEUTRAL" else "EMAها هم‌جهت نیستند.", 1.0))
    if s50 and s200:
        d = "BUY" if s50 > s200 and price > s50 else "SELL" if s50 < s200 and price < s50 else "NEUTRAL"
        votes.append(_vote("SMA Trend", d, 82 if d != "NEUTRAL" else 40, "ساختار SMA50/SMA200 هم‌جهت است." if d != "NEUTRAL" else "SMA50/SMA200 اجماع واضح ندارند.", 1.05))
    if r is not None:
        d = "BUY" if 50 <= r <= 68 else "SELL" if 32 <= r < 50 else "NEUTRAL"
        votes.append(_vote("RSI Momentum", d, 70 if d != "NEUTRAL" else 45, f"RSI برابر {r:.1f} است." , .9))
    if bb:
        low, mid, high = bb
        d = "BUY" if price > mid and price < high else "SELL" if price < mid and price > low else "NEUTRAL"
        votes.append(_vote("Bollinger", d, 68 if d != "NEUTRAL" else 42, "قیمت نسبت به باندهای بولینگر مومنتوم مناسبی دارد." if d != "NEUTRAL" else "قیمت در ناحیه خنثی بولینگر است.", .85))
    if dc:
        upper, lower = dc
        d = "BUY" if price > upper else "SELL" if price < lower else "NEUTRAL"
        votes.append(_vote("Donchian Breakout", d, 88 if d != "NEUTRAL" else 35, "شکست کانال دانچیان مشاهده شد." if d != "NEUTRAL" else "شکست معتبر دانچیان تأیید نشده است.", 1.05))
    if vr is not None:
        d = "BUY" if vr >= 1.8 and price >= closes[-2] else "SELL" if vr >= 1.8 and price < closes[-2] else "NEUTRAL"
        votes.append(_vote("Volume Breakout", d, 86 if d != "NEUTRAL" else 38, f"نسبت حجم به میانگین: {vr:.2f}x", 1.0))
    if a and price > 0:
        vol_pct = a / price * 100
        votes.append(_vote("Volatility", "BUY" if vol_pct >= .8 and price > closes[-2] else "NEUTRAL", 65 if vol_pct >= .8 else 40, f"ATR حدود {vol_pct:.2f}% قیمت است.", .8))
    return votes
