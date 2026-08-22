"""ثبت منابع تحلیلی خارجی با کنترل اعتبار و تازگی."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True, slots=True)
class SourcePolicy:
    name: str
    kind: str
    base_weight: float
    max_age_hours: int

DEFAULT_SOURCES = (
    SourcePolicy("Coinbase Institutional", "exchange_research", 0.95, 72),
    SourcePolicy("Kraken Research", "exchange_research", 0.95, 72),
    SourcePolicy("Binance Research", "exchange_research", 0.95, 72),
    SourcePolicy("Poursamadi / ErfTrade", "strategy_research", 0.90, 72),
)

def source_policy(name: str) -> SourcePolicy | None:
    for item in DEFAULT_SOURCES:
        if item.name.lower() == name.lower():
            return item
    return None

def freshness_multiplier(published_at: str, max_age_hours: int) -> float:
    try:
        dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
    except ValueError:
        return 0.0
    if age < 0 or age > max_age_hours:
        return 0.0
    return max(0.1, 1.0 - age / max_age_hours)
