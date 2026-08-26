"""
PACT-OS
Market Regime Engine
"""

from __future__ import annotations

from dataclasses import dataclass

from analysis.ema import calculate as ema


@dataclass(slots=True)
class MarketRegimeResult:

    regime: str
    bullish: bool
    bearish: bool
    ranging: bool
    confidence: float

    ema21: float
    ema50: float
    ema200: float


class MarketRegimeEngine:

    def evaluate(
        self,
        prices: list[float],
    ) -> MarketRegimeResult:

        if not prices:
            return MarketRegimeResult(
                regime="UNKNOWN",
                bullish=False,
                bearish=False,
                ranging=False,
                confidence=0.0,
                ema21=0.0,
                ema50=0.0,
                ema200=0.0,
            )

        if len(prices) < 21:
            price = prices[-1]
            return MarketRegimeResult(
                regime="UNKNOWN",
                bullish=False,
                bearish=False,
                ranging=False,
                confidence=0.0,
                ema21=price,
                ema50=price,
                ema200=price,
            )

        ema21 = ema(prices, 21)

        if len(prices) >= 50:
            ema50 = ema(prices, 50)
        else:
            ema50 = ema21

        if len(prices) >= 200:
            ema200 = ema(prices, 200)
        else:
            ema200 = ema50

        price = prices[-1]

        if (
            price > ema21
            and ema21 > ema50
            and ema50 > ema200
            and len(prices) >= 200
        ):
            return MarketRegimeResult(
                regime="BULL",
                bullish=True,
                bearish=False,
                ranging=False,
                confidence=90.0,
                ema21=ema21,
                ema50=ema50,
                ema200=ema200,
            )

        if (
            price < ema21
            and ema21 < ema50
            and ema50 < ema200
            and len(prices) >= 200
        ):
            return MarketRegimeResult(
                regime="BEAR",
                bullish=False,
                bearish=True,
                ranging=False,
                confidence=90.0,
                ema21=ema21,
                ema50=ema50,
                ema200=ema200,
            )

        return MarketRegimeResult(
            regime="RANGE",
            bullish=False,
            bearish=False,
            ranging=True,
            confidence=60.0,
            ema21=ema21,
            ema50=ema50,
            ema200=ema200,
        )
