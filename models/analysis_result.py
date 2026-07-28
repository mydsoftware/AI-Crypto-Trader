"""
PACT-OS
Analysis Result Model
"""

from dataclasses import dataclass


@dataclass(slots=True)
class AnalysisResult:

    symbol: str

    ema9: float
    ema21: float

    rsi: float

    macd: float
    signal_line: float
    histogram: float

    score: int
    signal: str

    ema_signal: str
    rsi_signal: str
    macd_signal: str