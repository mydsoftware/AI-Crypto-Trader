"""
PACT-OS - Market Scanner
"""

from __future__ import annotations

from exchange.tabdeal_client import TabdealClient
from market.watchlist import WATCHLIST
from models.ticker import Ticker


class MarketScanner:
    """
    Scan selected markets and return ticker objects.
    """

    def __init__(self, client: TabdealClient) -> None:
        self.client = client

    def scan(self) -> list[Ticker]:
        """
        Scan all symbols in WATCHLIST.
        """

        tickers: list[Ticker] = []

        for symbol in WATCHLIST:

            trades = self.client.trades(symbol, limit=1)

            if not trades:
                continue

            trade = trades[0]

            orderbook = self.client.depth(symbol, limit=5)

            ticker = Ticker(
                symbol=symbol,
                last_price=trade.price,
                best_bid=orderbook.best_bid,
                best_ask=orderbook.best_ask,
                spread=orderbook.spread,
                spread_percent=orderbook.spread_percent,
            )

            tickers.append(ticker)

        return tickers