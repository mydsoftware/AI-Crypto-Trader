"""اسکنر فرصت‌های خرید و حرکت‌های انفجاری بازار.

این ماژول فقط تحلیل می‌کند و هیچ سفارشی ارسال نمی‌کند.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(slots=True)
class MarketSnapshot:
    symbol: str
    price_change_pct: float
    volume_ratio: float
    momentum: float
    breakout: float
    liquidity_score: float
    trend_score: float
    risk_score: float


@dataclass(slots=True)
class Opportunity:
    symbol: str
    category: str
    score: float
    confidence: float
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class OpportunityScanner:
    """نمادها را رتبه‌بندی می‌کند؛ سیگنال را به‌عنوان تضمین سود تفسیر نمی‌کند."""

    def __init__(self, min_liquidity: float = 45.0) -> None:
        self.min_liquidity = min_liquidity

    def scan(self, snapshots: Iterable[MarketSnapshot]) -> list[Opportunity]:
        results: list[Opportunity] = []
        for item in snapshots:
            if item.liquidity_score < self.min_liquidity:
                continue

            # امتیاز فرصت خرید؛ وزن حرکت و حجم برای کشف آلت‌کوین‌های در حال شتاب بیشتر است.
            score = (
                item.trend_score * 0.20
                + item.momentum * 0.22
                + item.breakout * 0.18
                + min(item.volume_ratio * 20.0, 100.0) * 0.18
                + item.liquidity_score * 0.12
                + max(0.0, 100.0 - item.risk_score) * 0.10
            )
            score = max(0.0, min(100.0, score))
            reasons: list[str] = []
            warnings: list[str] = []

            if item.trend_score >= 70:
                reasons.append("روند صعودی قدرت مناسبی دارد.")
            if item.momentum >= 70:
                reasons.append("مومنتوم صعودی تقویت شده است.")
            if item.breakout >= 70:
                reasons.append("نشانه‌های شکست یا فشار خرید دیده می‌شود.")
            if item.volume_ratio >= 2:
                reasons.append(f"حجم حدود {item.volume_ratio:.1f} برابر میانگین است.")
            if item.price_change_pct >= 5:
                reasons.append(f"حرکت قیمت {item.price_change_pct:.1f}% شتاب گرفته است.")

            pump_score = (
                min(max(item.price_change_pct, 0.0) * 4.0, 100.0) * 0.30
                + min(item.volume_ratio * 25.0, 100.0) * 0.30
                + item.momentum * 0.20
                + item.breakout * 0.20
            )

            if pump_score >= 75:
                category = "PUMP_WATCH"
                reasons.append("شتاب غیرعادی قیمت/حجم؛ در فهرست پایش حرکت انفجاری قرار گرفت.")
                if item.risk_score >= 60:
                    warnings.append("ریسک نوسان شدید بالاست؛ این مورد به معنی پامپ قطعی نیست.")
            elif score >= 65:
                category = "BUY_CANDIDATE"
            else:
                category = "WATCH"

            if not reasons:
                reasons.append("شرایط هنوز برای ورود با کیفیت کافی نیست؛ فقط تحت پایش است.")

            confidence = max(0.0, min(100.0, score - item.risk_score * 0.15))
            results.append(Opportunity(item.symbol, category, round(score, 2), round(confidence, 2), reasons, warnings))

        return sorted(results, key=lambda x: (x.category == "PUMP_WATCH", x.score), reverse=True)
