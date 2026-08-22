"""محاسبه‌گر اندیکاتورهای پایه برای موتور تحلیل چنداستراتژی."""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(slots=True)
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


def sma(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def ema(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    value = sum(values[:period]) / period
    multiplier = 2 / (period + 1)
    for price in values[period:]:
        value = (price - value) * multiplier + value
    return value


def atr(candles: list[Candle], period: int = 14) -> float | None:
    if len(candles) < period + 1:
        return None
    trs: list[float] = []
    for i in range(1, len(candles)):
        c, p = candles[i], candles[i - 1]
        trs.append(max(c.high - c.low, abs(c.high - p.close), abs(c.low - p.close)))
    return sum(trs[-period:]) / period


def rsi(values: list[float], period: int = 14) -> float | None:
    if len(values) < period + 1:
        return None
    changes = [values[i] - values[i - 1] for i in range(1, len(values))]
    gains = [max(x, 0) for x in changes[-period:]]
    losses = [max(-x, 0) for x in changes[-period:]]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    return 100 - (100 / (1 + avg_gain / avg_loss))


def bollinger(values: list[float], period: int = 20, deviations: float = 2.0) -> tuple[float, float, float] | None:
    if len(values) < period:
        return None
    window = values[-period:]
    middle = sum(window) / period
    variance = sum((x - middle) ** 2 for x in window) / period
    sd = sqrt(variance)
    return middle - deviations * sd, middle, middle + deviations * sd


def volume_ratio(candles: list[Candle], period: int = 20) -> float | None:
    if len(candles) < period + 1:
        return None
    average = sum(c.volume for c in candles[-period - 1:-1]) / period
    return candles[-1].volume / average if average else None


def donchian(candles: list[Candle], period: int = 20) -> tuple[float, float] | None:
    if len(candles) < period + 1:
        return None
    window = candles[-period - 1:-1]
    return max(c.high for c in window), min(c.low for c in window)
