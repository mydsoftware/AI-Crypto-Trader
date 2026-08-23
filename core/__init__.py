"""هسته موتور تحلیل و داده."""
from .data_engine import DataEngine, MarketSnapshot
from .technical import Evidence, generate_technical_evidence, technical_score
from .regime import MarketRegime, detect_regime
from .paper_trading import PaperLedger, PaperTrade

def __getattr__(name: str):
    if name in ("OpportunityEngine", "FinalOpportunity"):
        from .opportunity_engine import OpportunityEngine, FinalOpportunity
        return OpportunityEngine if name == "OpportunityEngine" else FinalOpportunity
    raise AttributeError(name)

__all__ = [
    "DataEngine", "MarketSnapshot",
    "OpportunityEngine", "FinalOpportunity",
    "Evidence", "generate_technical_evidence", "technical_score",
    "MarketRegime", "detect_regime",
    "PaperLedger", "PaperTrade",
]
