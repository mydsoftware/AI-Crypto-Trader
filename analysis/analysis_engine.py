"""
PACT-OS
Analysis Engine
"""

from __future__ import annotations

from analysis.breakout import BreakoutEngine
from analysis.breakout_filter import BreakoutFilter
from analysis.indicators import IndicatorPipeline
from analysis.pullback import PullbackEngine
from analysis.signal_engine import evaluate
from analysis.support_resistance import (
    SupportResistanceEngine,
)
from analysis.volume_engine import (
    VolumeEngine,
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

        self.breakout = (
            BreakoutEngine()
        )

        self.breakout_filter = (
            BreakoutFilter()
        )

        self.pullback = (
            PullbackEngine()
        )

        self.volume = (
            VolumeEngine()
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

        current_price = prices[-1]

        breakout = self.breakout.evaluate(

            current_price=current_price,

            support=sr.support,

            resistance=sr.resistance,
        )

        if breakout.breakout_up:

            breakout_filter = (
                self.breakout_filter.validate(
                    current_price=current_price,
                    level=sr.resistance,
                )
            )

        elif breakout.breakout_down:

            breakout_filter = (
                self.breakout_filter.validate(
                    current_price=current_price,
                    level=sr.support,
                )
            )

        else:

            breakout_filter = (
                self.breakout_filter.validate(
                    current_price=current_price,
                    level=current_price,
                )
            )

        if breakout.breakout_up:

            pullback = self.pullback.evaluate(

                current_price=current_price,

                level=sr.resistance,
            )

        elif breakout.breakout_down:

            pullback = self.pullback.evaluate(

                current_price=current_price,

                level=sr.support,
            )

        else:

            pullback = self.pullback.evaluate(

                current_price=current_price,

                level=current_price,
            )

        # ======================================
        # Volume Analysis
        # (Temporary until Repository supports
        # real candle volume)
        # ======================================

        volumes = [1.0] * len(prices)

        volume = self.volume.evaluate(
            volumes,
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
            # Breakout
            # ======================================

            breakout_up=breakout.breakout_up,

            breakout_down=breakout.breakout_down,

            breakout_status=breakout.status,

            # ======================================
            # Breakout Filter
            # ======================================

            breakout_valid=(
                breakout_filter.valid
            ),

            breakout_distance_percent=(
                breakout_filter.distance_percent
            ),

            breakout_threshold=(
                breakout_filter.threshold_percent
            ),

            # ======================================
            # Pullback
            # ======================================

            pullback_detected=(
                pullback.detected
            ),

            pullback_status=(
                pullback.status
            ),

            pullback_distance_percent=(
                pullback.distance_percent
            ),

            # ======================================
            # Volume
            # ======================================

            current_volume=(
                volume.current_volume
            ),

            average_volume=(
                volume.average_volume
            ),

            volume_ratio=(
                volume.ratio
            ),

            high_volume=(
                volume.high_volume
            ),

            volume_status=(
                volume.status
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