"""
موتور مستقل پورصمدی — سه رأی جداگانه وارد Ensemble می‌شوند.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from exchange.adapters.base import OHLCV
from scanner.ensemble_engine import StrategyVote

from .pro_btb import vote_pro_btb
from .sp2l import vote_sp2l
from .micromap import vote_micromap


@dataclass
class PoursamadiResult:
    votes: list[StrategyVote] = field(default_factory=list)
    summary: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "votes": [
                {
                    "name": v.name,
                    "direction": v.direction,
                    "score": round(v.score, 1),
                    "confidence": round(v.score / 100, 2),
                    "reason": v.reason,
                }
                for v in self.votes
            ],
            "summary": self.summary,
        }


class PoursamadiEngine:
    """تولید رأی‌های مستقل Pro BTB / SP2L / MicroMAP."""

    def analyze(self, candles: list[OHLCV]) -> PoursamadiResult:
        votes = [
            vote_pro_btb(candles),
            vote_sp2l(candles),
            vote_micromap(candles),
        ]
        summary = {v.name: f"{v.direction} {v.score/100:.2f}" for v in votes}
        return PoursamadiResult(votes=votes, summary=summary)
