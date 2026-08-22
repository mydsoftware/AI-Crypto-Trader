"""لایه استاندارد جمع‌آوری شواهد خارجی برای موتور تحلیل.

منابع خارجی فقط «شاهد» هستند و به تنهایی سیگنال خرید/فروش ایجاد نمی‌کنند.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class EvidenceDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


@dataclass(slots=True)
class ExternalEvidence:
    source: str
    title: str
    url: str
    published_at: str
    direction: EvidenceDirection
    relevance: float
    confidence: float
    summary: str
    tags: list[str] = field(default_factory=list)

    @property
    def weight(self) -> float:
        return max(0.0, min(1.0, self.relevance)) * max(0.0, min(1.0, self.confidence))


@dataclass(slots=True)
class ExternalConsensus:
    bullish: float
    bearish: float
    neutral: float
    evidence_count: int
    sources: list[str]


def build_consensus(evidence: list[ExternalEvidence]) -> ExternalConsensus:
    """اجماع منابع را نرمال می‌کند؛ داده قدیمی یا بی‌ربط وزن کمی می‌گیرد."""
    totals = {d: 0.0 for d in EvidenceDirection}
    sources: list[str] = []
    for item in evidence:
        totals[item.direction] += item.weight
        if item.source not in sources:
            sources.append(item.source)
    total = sum(totals.values())
    if total <= 0:
        return ExternalConsensus(0, 0, 0, 0, sources)
    return ExternalConsensus(
        round(totals[EvidenceDirection.BULLISH] / total * 100, 2),
        round(totals[EvidenceDirection.BEARISH] / total * 100, 2),
        round(totals[EvidenceDirection.NEUTRAL] / total * 100, 2),
        len(evidence),
        sources,
    )


def fresh_evidence(evidence: list[ExternalEvidence], max_age_hours: int = 72) -> list[ExternalEvidence]:
    """برای جلوگیری از اثرگذاری تحلیل‌های قدیمی، شواهد منقضی را حذف می‌کند."""
    now = datetime.now(timezone.utc)
    result: list[ExternalEvidence] = []
    for item in evidence:
        try:
            published = datetime.fromisoformat(item.published_at.replace("Z", "+00:00"))
            age = (now - published).total_seconds() / 3600
            if 0 <= age <= max_age_hours:
                result.append(item)
        except ValueError:
            continue
    return result
