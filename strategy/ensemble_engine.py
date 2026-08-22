"""موتور اجماع استراتژی‌ها برای دستیار معامله‌گر.

هدف این ماژول ترکیب خانواده‌های مستقل تحلیل است، نه ادعای وجود یک
اندیکاتور جادویی. هر سیگنال باید روی داده گذشته قابل بک‌تست باشد.
این موتور فقط پیشنهاد ورود/خروج می‌دهد و هیچ سفارش واقعی ارسال نمی‌کند.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from statistics import mean, pstdev
from typing import Sequence


@dataclass(slots=True)
class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(slots=True)
class StrategyVote:
    name: str
    score: float
    direction: str
    reason: str


@dataclass(slots=True)
class TradePlan:
    symbol: str
    direction: str
    score: float
    entry_low: float
    entry_high: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    risk_reward: float
    confidence: float
    votes: list[StrategyVote] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _sma(values: Sequence[float], n: int) -> float:
    return mean(values[-n:]) if len(values) >= n else mean(values)


def _ema(values: Sequence[float], n: int) -> float:
    if not values:
        return 0.0
    k = 2 / (n + 1)
    result = values[0]
    for value in values[1:]:
        result = value * k + result * (1 - k)
    return result


def _rsi(values: Sequence[float], n: int = 14) -> float:
    if len(values) < n + 1:
        return 50.0
    gains = []
    losses = []
    for a, b in zip(values[-n - 1:-1], values[-n:]):
        delta = b - a
        gains.append(max(delta, 0))
        losses.append(max(-delta, 0))
    avg_gain = mean(gains)
    avg_loss = mean(losses)
    if avg_loss == 0:
        return 100.0
    return 100 - 100 / (1 + avg_gain / avg_loss)


def _atr(candles: Sequence[Candle], n: int = 14) -> float:
    if len(candles) < 2:
        return 0.0
    trs = []
    for previous, current in zip(candles[-n - 1:-1], candles[-n:]):
        trs.append(max(current.high - current.low, abs(current.high - previous.close), abs(current.low - previous.close)))
    return mean(trs) if trs else 0.0


def _adx_proxy(candles: Sequence[Candle], n: int = 14) -> float:
    """برآورد ساده قدرت روند؛ برای تأیید نهایی باید با ADX کامل جایگزین شود."""
    if len(candles) < n * 2:
        return 0.0
    closes = [c.close for c in candles]
    fast = _sma(closes, n)
    slow = _sma(closes, n * 2)
    return min(100.0, abs(fast - slow) / max(slow, 1e-12) * 1000)


def _bollinger(values: Sequence[float], n: int = 20, mult: float = 2.0) -> tuple[float, float, float]:
    window = values[-n:] if len(values) >= n else values
    middle = mean(window)
    deviation = pstdev(window) if len(window) > 1 else 0.0
    return middle - mult * deviation, middle, middle + mult * deviation


def _vwap(candles: Sequence[Candle], n: int = 50) -> float:
    window = candles[-n:]
    total_volume = sum(c.volume for c in window)
    return sum(((c.high + c.low + c.close) / 3) * c.volume for c in window) / total_volume if total_volume else window[-1].close


def _donchian(candles: Sequence[Candle], n: int = 20) -> tuple[float, float]:
    window = candles[-n - 1:-1]
    return max(c.high for c in window), min(c.low for c in window)


def _supertrend_bias(candles: Sequence[Candle]) -> int:
    """فیلتر جهت Supertrend سبک؛ ATR برای فاصله حدضرر استفاده می‌شود."""
    atr = _atr(candles, 10)
    if not atr:
        return 0
    last = candles[-1]
    midpoint = (last.high + last.low) / 2
    if last.close > midpoint + atr * 0.5:
        return 1
    if last.close < midpoint - atr * 0.5:
        return -1
    return 0


class EnsembleStrategyEngine:
    """اجماع چند خانواده استراتژی را به یک Trade Plan قابل توضیح تبدیل می‌کند."""

    STRATEGIES = (
        "EMA Trend",
        "SMA 50/200 Trend",
        "RSI Mean Reversion",
        "MACD Momentum",
        "Bollinger Mean Reversion",
        "Donchian Breakout",
        "VWAP Reclaim",
        "Volume Breakout",
        "Supertrend",
        "ADX Regime",
        "Fibonacci Pullback",
        "Volatility Expansion",
    )

    def analyze(self, symbol: str, candles: Sequence[Candle]) -> TradePlan | None:
        if len(candles) < 60:
            return None
        closes = [c.close for c in candles]
        last = candles[-1]
        price = last.close
        atr = _atr(candles)
        if atr <= 0:
            return None

        ema9, ema21 = _ema(closes, 9), _ema(closes, 21)
        sma50, sma200 = _sma(closes, 50), _sma(closes, min(200, len(closes)))
        rsi = _rsi(closes)
        macd = _ema(closes, 12) - _ema(closes, 26)
        macd_signal = _ema([_ema(closes[:i], 12) - _ema(closes[:i], 26) for i in range(26, len(closes) + 1)], 9) if len(closes) >= 35 else macd
        lower, middle, upper = _bollinger(closes)
        vwap = _vwap(candles)
        high20, low20 = _donchian(candles)
        adx = _adx_proxy(candles)
        supertrend = _supertrend_bias(candles)
        avg_volume = _sma([c.volume for c in candles], 20)
        volume_ratio = last.volume / avg_volume if avg_volume else 1.0

        votes: list[StrategyVote] = []
        def add(name: str, score: float, direction: str, reason: str) -> None:
            votes.append(StrategyVote(name, max(-100, min(100, score)), direction, reason))

        add("EMA Trend", 75 if ema9 > ema21 else -75, "BUY" if ema9 > ema21 else "SELL", "EMA کوتاه‌مدت نسبت به EMA بلندتر بررسی شد.")
        add("SMA 50/200 Trend", 70 if sma50 > sma200 else -70, "BUY" if sma50 > sma200 else "SELL", "فیلتر روند میان‌مدت/بلندمدت.")
        add("RSI Mean Reversion", 65 if 30 < rsi < 45 else (-55 if rsi > 72 else 15), "BUY" if 30 < rsi < 45 else "WAIT", f"RSI فعلی {rsi:.1f} است.")
        add("MACD Momentum", 70 if macd > macd_signal else -65, "BUY" if macd > macd_signal else "SELL", "مومنتوم MACD بررسی شد.")
        add("Bollinger Mean Reversion", 65 if price <= middle and price > lower else (-45 if price > upper else 10), "BUY" if price <= middle and price > lower else "WAIT", "موقعیت قیمت نسبت به باندهای بولینگر.")
        add("Donchian Breakout", 90 if price > high20 else (-70 if price < low20 else 5), "BUY" if price > high20 else "WAIT", "شکست محدوده ۲۰ کندل قبلی.")
        add("VWAP Reclaim", 65 if price > vwap else -45, "BUY" if price > vwap else "SELL", "قیمت نسبت به VWAP.")
        add("Volume Breakout", 85 if volume_ratio >= 2 and price > closes[-2] else 0, "BUY" if volume_ratio >= 2 and price > closes[-2] else "WAIT", f"نسبت حجم به میانگین: {volume_ratio:.2f}x.")
        add("Supertrend", 60 if supertrend > 0 else (-60 if supertrend < 0 else 0), "BUY" if supertrend > 0 else "WAIT", "فیلتر جهت Supertrend.")
        add("ADX Regime", 45 if adx >= 25 else 0, "BUY" if adx >= 25 else "WAIT", f"قدرت روند برآوردشده: {adx:.1f}.")

        recent_high = max(c.high for c in candles[-60:])
        recent_low = min(c.low for c in candles[-60:])
        fib_618 = recent_high - (recent_high - recent_low) * 0.618
        add("Fibonacci Pullback", 60 if fib_618 * 0.995 <= price <= fib_618 * 1.005 else 10, "BUY" if fib_618 * 0.995 <= price <= fib_618 * 1.005 else "WAIT", "ناحیه اصلاح 61.8٪ فیبوناچی بررسی شد.")

        atr_now = _atr(candles, 14)
        atr_old = _atr(candles[:-10], 14)
        add("Volatility Expansion", 70 if atr_old and atr_now > atr_old * 1.25 and price > middle else 0, "BUY" if atr_old and atr_now > atr_old * 1.25 and price > middle else "WAIT", "افزایش نوسان همراه با جهت قیمت بررسی شد.")

        buy_votes = [v for v in votes if v.score > 0 and v.direction == "BUY"]
        sell_votes = [v for v in votes if v.score < 0]
        raw = sum(v.score for v in votes) / len(votes)
        agreement = len(buy_votes) / len(votes)
        score = max(0.0, min(100.0, 50 + raw / 2))

        # اجماع ضعیف یعنی خروجی ورود نداریم؛ این بخش از تولید سیگنال اجباری جلوگیری می‌کند.
        if agreement < 0.58 or score < 60:
            return None

        entry_low = min(price, price - atr * 0.25)
        entry_high = price + atr * 0.15
        stop = price - atr * 1.5
        risk = max(price - stop, atr * 0.1)
        tp1 = price + risk * 2
        tp2 = price + risk * 3
        rr = (tp2 - price) / risk
        confidence = max(0.0, min(100.0, 55 + agreement * 35 + min(adx, 40) * 0.25))

        reasons = [v.reason for v in buy_votes if v.score >= 60]
        warnings: list[str] = []
        if rsi > 70:
            warnings.append("RSI در ناحیه اشباع خرید است؛ ورود تعقیبی پرریسک‌تر است.")
        if volume_ratio > 4:
            warnings.append("حجم بسیار غیرعادی است؛ احتمال نوسان و برگشت شدید وجود دارد.")
        if adx < 20:
            warnings.append("قدرت روند پایین است؛ احتمال نوسان خنثی بیشتر است.")

        return TradePlan(symbol, "BUY", round(score, 2), entry_low, entry_high, stop, tp1, tp2, round(rr, 2), round(confidence, 2), votes, reasons, warnings)
