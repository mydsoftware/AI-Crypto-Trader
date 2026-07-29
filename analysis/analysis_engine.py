"""
PACT-OS
Analysis Engine
"""

from __future__ import annotations

from analysis.indicators import IndicatorPipeline
from analysis.signal_engine import evaluate

from config import HISTORY_LIMIT

from database.database import Database

from models.analysis_result import AnalysisResult


class AnalysisEngine:

    def __init__(self, database: Database):

        self.database = database

    def analyze(self, symbol: str) -> AnalysisResult | None:

        prices = self.database.last_prices(
            symbol,
            limit=HISTORY_LIMIT,
        )

        if len(prices) < 35:
            return None

        indicators = IndicatorPipeline.from_prices(
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

            symbol=symbol,

            ema9=indicators.ema9,
            ema21=indicators.ema21,

            rsi=indicators.rsi,

            macd=indicators.macd,
            signal_line=indicators.signal,
            histogram=indicators.histogram,

            score=signal_result["score"],
            signal=signal_result["signal"],

            ema_signal=signal_result["details"]["ema"],
            rsi_signal=signal_result["details"]["rsi"],
            macd_signal=signal_result["details"]["macd"],
        )