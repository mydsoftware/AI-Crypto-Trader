"""
PACT-OS
Historical Data Manager
"""

from __future__ import annotations

from database.repository import CandleRepository


class HistoricalDataManager:

    def __init__(
        self,
        repository: CandleRepository,
    ) -> None:

        self.repository = repository

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

        return self.repository.last_snapshots(
            symbol=symbol,
            limit=limit,
        )

    def available(
        self,
        symbol: str,
        minimum: int,
    ) -> bool:

        prices = self.prices(
            symbol=symbol,
            limit=minimum,
        )

        return len(prices) >= minimum

    def count(
        self,
        symbol: str,
    ) -> int:

        return self.repository.count(
            symbol=symbol,
        )