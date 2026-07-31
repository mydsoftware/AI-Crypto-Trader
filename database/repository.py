"""
PACT-OS
Candle Repository
"""

from __future__ import annotations

from database.database import Database

from models.trade import Trade


class CandleRepository:

    def __init__(
        self,
        database: Database,
    ):

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

    def last_volumes(
        self,
        symbol: str,
        limit: int,
    ) -> list[float]:

        return self.database.last_volumes(
            symbol=symbol,
            limit=limit,
        )

    def last_trades(
        self,
        symbol: str,
        limit: int,
    ) -> list[Trade]:

        return self.database.last_trades(
            symbol=symbol,
            limit=limit,
        )