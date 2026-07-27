"""
PACT-OS - Market Repository
"""

from __future__ import annotations

import time

from sqlalchemy.orm import Session

from database.models import MarketSnapshot
from models.ticker import Ticker


class MarketRepository:
    """
    Repository for MarketSnapshot records.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, ticker: Ticker) -> None:
        """
        Save one market snapshot.
        """

        snapshot = MarketSnapshot(
            symbol=ticker.symbol,
            last_price=ticker.last_price,
            best_bid=ticker.best_bid,
            best_ask=ticker.best_ask,
            spread=ticker.spread,
            spread_percent=ticker.spread_percent,
            timestamp=int(time.time()),
        )

        self._session.add(snapshot)
        self._session.commit()

    def save_all(self, tickers: list[Ticker]) -> None:
        """
        Save all tickers.
        """

        now = int(time.time())

        snapshots = [
            MarketSnapshot(
                symbol=ticker.symbol,
                last_price=ticker.last_price,
                best_bid=ticker.best_bid,
                best_ask=ticker.best_ask,
                spread=ticker.spread,
                spread_percent=ticker.spread_percent,
                timestamp=now,
            )
            for ticker in tickers
        ]

        self._session.add_all(snapshots)
        self._session.commit()