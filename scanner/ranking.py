"""رتبه‌بندی فرصت‌ها با ترکیب تحلیل، اجماع و هزینه معامله."""
from __future__ import annotations
from dataclasses import dataclass
from .cost_model import CostModel

@dataclass(slots=True)
class OpportunityScore:
    symbol: str
    final_score: float
    category: str
    reasons: list[str]
    warnings: list[str]


def rank(symbol: str, technical: float, timeframe: float, external: float, liquidity: float, risk: float, expected_move: float, cost: CostModel | None = None) -> OpportunityScore:
    cost = cost or CostModel()
    edge = expected_move - cost.minimum_edge()
    score = technical * .30 + timeframe * .20 + external * .15 + liquidity * .15 + max(0, 100-risk) * .20
    if edge <= 0:
        score *= .55
    score = max(0, min(100, score))
    warnings = []
    reasons = []
    if edge > 0: reasons.append("حرکت مورد انتظار از هزینه تخمینی معامله بزرگ‌تر است.")
    else: warnings.append("مزیت مورد انتظار پس از هزینه معامله کافی نیست.")
    if liquidity < 50: warnings.append("نقدشوندگی پایین است.")
    if risk >= 70: warnings.append("ریسک بازار بالا است.")
    category = "BUY" if score >= 75 and edge > 0 else "WATCH" if score >= 55 else "WAIT"
    return OpportunityScore(symbol, round(score, 2), category, reasons, warnings)
