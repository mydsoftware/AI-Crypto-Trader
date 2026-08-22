"""ترکیب رأی استراتژی‌ها در چند تایم‌فریم."""
from __future__ import annotations
from dataclasses import dataclass
from .ensemble_engine import StrategyVote
from .strategy_votes import generate_votes
from .indicators import Candle

@dataclass(slots=True)
class TimeframeResult:
    timeframe: str
    votes: list[StrategyVote]


def analyze_timeframes(frames: dict[str, list[Candle]]) -> list[TimeframeResult]:
    """برای هر تایم‌فریم رأی مستقل تولید می‌کند تا رأی تایم‌فریم‌ها قابل مشاهده و بک‌تست باشد."""
    order = {"5m": 1, "15m": 2, "1h": 3, "4h": 4, "1d": 5}
    return [TimeframeResult(tf, generate_votes(candles)) for tf, candles in sorted(frames.items(), key=lambda x: order.get(x[0], 99))]


def timeframe_consensus(results: list[TimeframeResult]) -> dict[str, float]:
    buy = sell = total = 0.0
    for result in results:
        weight = {"5m": .7, "15m": .9, "1h": 1.0, "4h": 1.15, "1d": 1.25}.get(result.timeframe, 1.0)
        for vote in result.votes:
            if vote.direction == "BUY": buy += vote.score * vote.reliability * weight
            elif vote.direction == "SELL": sell += vote.score * vote.reliability * weight
            total += vote.score * vote.reliability * weight
    return {"buy": round(buy / total * 100, 2) if total else 0.0, "sell": round(sell / total * 100, 2) if total else 0.0}
