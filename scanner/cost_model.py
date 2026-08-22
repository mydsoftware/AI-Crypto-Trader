"""مدل هزینه و اسلیپیج برای جلوگیری از سیگنال‌های غیرواقعی."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True)
class CostModel:
    fee_bps: float = 10.0
    slippage_bps: float = 5.0
    spread_bps: float = 2.0

    @property
    def round_trip_rate(self) -> float:
        return 2.0 * (self.fee_bps + self.slippage_bps + self.spread_bps) / 10000.0

    def minimum_edge(self, safety_multiplier: float = 1.25) -> float:
        return self.round_trip_rate * safety_multiplier

    def net_return(self, gross_return: float) -> float:
        return gross_return - self.round_trip_rate
