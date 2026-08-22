"""موتور اجماع استراتژی‌ها برای تولید نقطه ورود و خروج تحلیلی.

این ماژول سفارش ارسال نمی‌کند و خروجی آن صرفاً طرح تحلیلی است.
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass(slots=True)
class StrategyVote:
    name: str
    direction: str  # BUY / SELL / NEUTRAL
    score: float
    reason: str
    reliability: float = 1.0


@dataclass(slots=True)
class TradePlan:
    direction: str
    confidence: float
    entry_low: float | None
    entry_high: float | None
    stop_loss: float | None
    take_profit_1: float | None
    take_profit_2: float | None
    risk_reward: float | None
    strategy_agreement: float
    reasons: list[str]
    warnings: list[str]


class EnsembleEngine:
    """رأی استراتژی‌ها را با وزن اعتماد ترکیب می‌کند."""

    def build_plan(
        self,
        votes: list[StrategyVote],
        price: float,
        atr: float | None = None,
        min_agreement: float = 0.62,
    ) -> TradePlan:
        if not votes or price <= 0:
            return TradePlan("WAIT", 0, None, None, None, None, None, None, 0, [], ["داده کافی برای اجماع وجود ندارد."])

        buy = sum(v.reliability * max(v.score, 0) for v in votes if v.direction == "BUY")
        sell = sum(v.reliability * max(v.score, 0) for v in votes if v.direction == "SELL")
        total = buy + sell
        if total <= 0:
            return TradePlan("WAIT", 0, None, None, None, None, None, None, 0, [], ["استراتژی‌ها اجماع قابل اتکایی ندارند."])

        direction = "BUY" if buy >= sell else "SELL"
        dominant = buy if direction == "BUY" else sell
        agreement = dominant / total
        supporting = [v for v in votes if v.direction == direction]
        reasons = [v.reason for v in supporting if v.reason]
        warnings = []

        if agreement < min_agreement:
            return TradePlan("WAIT", round(agreement * 100, 2), None, None, None, None, None, None, round(agreement * 100, 2), reasons, ["اجماع استراتژی‌ها به حداقل لازم نرسیده است."])

        # ATR برای حد ضرر و اهداف ترجیح داده می‌شود؛ در نبود ATR فقط طرح ورود تولید می‌شود.
        if atr is None or atr <= 0:
            warnings.append("ATR در دسترس نیست؛ حد ضرر و اهداف باید بعد از دریافت نوسان واقعی محاسبه شوند.")
            return TradePlan(direction, round(agreement * 100, 2), price, price, None, None, None, None, round(agreement * 100, 2), reasons, warnings)

        if direction == "BUY":
            stop = price - 1.5 * atr
            risk = price - stop
            tp1 = price + 2.0 * risk
            tp2 = price + 3.0 * risk
        else:
            stop = price + 1.5 * atr
            risk = stop - price
            tp1 = price - 2.0 * risk
            tp2 = price - 3.0 * risk

        confidence = min(99.0, agreement * 100)
        return TradePlan(direction, round(confidence, 2), price * 0.9975, price * 1.0025, stop, tp1, tp2, 2.0, round(agreement * 100, 2), reasons, warnings)


def strategy_consensus(votes: list[StrategyVote]) -> dict[str, float]:
    """خلاصه اجماع برای نمایش در داشبورد."""
    if not votes:
        return {"buy": 0.0, "sell": 0.0, "neutral": 0.0}
    weighted = {"BUY": [], "SELL": [], "NEUTRAL": []}
    for vote in votes:
        weighted.setdefault(vote.direction, []).append(vote.score * vote.reliability)
    return {"buy": round(mean(weighted["BUY"]) if weighted["BUY"] else 0, 2), "sell": round(mean(weighted["SELL"]) if weighted["SELL"] else 0, 2), "neutral": round(mean(weighted["NEUTRAL"]) if weighted["NEUTRAL"] else 0, 2)}
