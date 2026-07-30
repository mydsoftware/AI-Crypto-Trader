"""
PACT-OS
Analysis Result Model
"""

from dataclasses import dataclass


@dataclass(slots=True)
class AnalysisResult:

    # ==========================================
    # Symbol
    # ==========================================

    symbol: str

    # ==========================================
    # Indicators
    # ==========================================

    ema9: float
    ema21: float

    rsi: float

    macd: float
    signal_line: float
    histogram: float

    # ==========================================
    # Support / Resistance
    # ==========================================

    support: float
    resistance: float

    distance_to_support: float
    distance_to_resistance: float

    # ==========================================
    # Breakout
    # ==========================================

    breakout_up: bool
    breakout_down: bool

    breakout_status: str

    # ==========================================
    # Breakout Filter
    # ==========================================

    breakout_valid: bool

    breakout_distance_percent: float

    breakout_threshold: float

    # ==========================================
    # Pullback
    # ==========================================

    pullback_detected: bool

    pullback_status: str

    pullback_distance_percent: float

    # ==========================================
    # Volume
    # ==========================================

    current_volume: float

    average_volume: float

    volume_ratio: float

    high_volume: bool

    volume_status: str

    # ==========================================
    # Final Signal
    # ==========================================

    score: int
    signal: str

    ema_signal: str
    rsi_signal: str
    macd_signal: str