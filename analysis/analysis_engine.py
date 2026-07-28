"""
PACT-OS
Analysis Engine
"""

from __future__ import annotations

from analysis.ema import calculate as ema
from analysis.macd import calculate as macd
from analysis.rsi import calculate as rsi
from analysis.signal_engine import evaluate

from config import HISTORY_LIMIT

from database.database import Database


class AnalysisEngine:

    def __init__(self, database: Database):

        self.database = database

    def analyze(self, symbol: str) -> dict | None:

        prices = self.database.last_prices(
            symbol,
            limit=HISTORY_LIMIT,
        )

        if len(prices) < 35:
            return None

        ema9 = ema(prices, 9)
        ema21 = ema(prices, 21)

        rsi14 = rsi(prices, 14)

        macd_result = macd(prices)

        signal = evaluate(
            ema9=ema9,
            ema21=ema21,
            rsi14=rsi14,
            macd=macd_result["macd"],
            signal=macd_result["signal"],
        )

        return {

            "symbol": symbol,

            "ema9": ema9,
            "ema21": ema21,

            "rsi": rsi14,

            "macd": macd_result["macd"],
            "signal_line": macd_result["signal"],
            "histogram": macd_result["histogram"],

            "score": signal["score"],
            "signal": signal["signal"],

            "details": signal["details"],
        }