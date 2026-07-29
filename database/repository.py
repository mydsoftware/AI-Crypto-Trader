"""
PACT-OS
Candle Repository
"""

from __future__ import annotations

from database.database import Database


class CandleRepository:

    def __init__(self, database: Database):

        self.database = database

    def last_prices(
        self,
        symbol: str,
        limit: int,
    ) -> list[float]:

        return self.database.last_prices(
            symbol=symbol,
            limit=limit,
        )