"""
PACT-OS
Analysis Engine
"""

from __future__ import annotations

from analysis.indicators import IndicatorPipeline
from analysis.signal_engine import evaluate
from analysis.support_resistance import (
    SupportResistanceEngine,
)

from config import HISTORY_LIMIT

from database.repository import CandleRepository

from models.analysis_result import AnalysisResult


class AnalysisEngine:

    def __init__(
        self,
        repository: CandleRepository,
    ):

        self.repository = repository

        self.support_resistance = (
            SupportResistanceEngine()
        )

    def analyze(
        self,
        symbol: str,
    ) -> AnalysisResult | None:

        prices = self.repository.last_prices(
            symbol=symbol,
            limit=HISTORY_LIMIT,
        )

        if len(prices) < 35:
            return None

        indicators = IndicatorPipeline.from_prices(
            prices,
        )

        sr = self.support_resistance.calculate(
            prices,
        )

        signal_result = evaluate(
            ema9=indicators.ema9,
            ema21=indicators.ema21,
            rsi14=indicators.rsi,
            macd=indicators.macd,
            signal=indicators.signal,
        )

        return AnalysisResult(

            # ======================================
            # Symbol
            # ======================================

            symbol=symbol,

            # ======================================
            # Indicators
            # ======================================

            ema9=indicators.ema9,
            ema21=indicators.ema21,

            rsi=indicators.rsi,

            macd=indicators.macd,
            signal_line=indicators.signal,
            histogram=indicators.histogram,

            # ======================================
            # Support / Resistance
            # ======================================

            support=sr.support,
            resistance=sr.resistance,

            distance_to_support=(
                sr.distance_to_support
            ),

            distance_to_resistance=(
                sr.distance_to_resistance
            ),

            # ======================================
            # Final Result
            # ======================================

            score=signal_result["score"],
            signal=signal_result["signal"],

            ema_signal=signal_result["details"]["ema"],
            rsi_signal=signal_result["details"]["rsi"],
            macd_signal=signal_result["details"]["macd"],
        )