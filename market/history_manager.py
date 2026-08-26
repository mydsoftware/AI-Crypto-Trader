"""
PACT-OS
Historical Data Manager
"""

from __future__ import annotations

from database.repository import CandleRepository
from market.history_cache import HistoryCache
from market.timeframe_aggregator import TimeframeAggregator


class HistoryManager:

    def __init__(
        self,
        repository: CandleRepository,
    ) -> None:

        self.repository = repository
        self.cache = HistoryCache()
        self.aggregator = TimeframeAggregator()

    def prices(
        self,
        symbol: str,
        limit: int = 500,
    ) -> list[float]:

        return self.repository.last_prices(
            symbol=symbol,
            limit=limit,
        )

    def volumes(
        self,
        symbol: str,
        limit: int = 500,
    ) -> list[float]:

        return self.repository.last_volumes(
            symbol=symbol,
            limit=limit,
        )

    def candles(
        self,
        symbol: str,
        limit: int = 500,
    ):

        cached = self.cache.get(symbol)

        if cached is not None:
            return cached

        snapshots = self.repository.last_snapshots(
            symbol=symbol,
            limit=limit,
        )

        candles = self.aggregator.build_1m(
            snapshots
        )

        self.cache.set(
            symbol,
            candles,
        )

        return candles

    def available(
        self,
        symbol: str,
        minimum: int,
    ) -> bool:

        return len(
            self.candles(
                symbol=symbol,
                limit=minimum,
            )
        ) >= minimum

    def count(
        self,
        symbol: str,
    ) -> int:

        return self.repository.count(
            symbol=symbol,
        )


# Backward-compatible alias for existing callers.
HistoricalDataManager = HistoryManager
