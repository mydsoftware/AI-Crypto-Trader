"""
PACT-OS - Tabdeal Client
"""

from __future__ import annotations

from tabdeal.spot import Spot

from models.trade import Trade
from models.orderbook import OrderBook


class TabdealClient:
    """Wrapper around the official Tabdeal Spot SDK."""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
    ) -> None:

        self._client = Spot(
            api_key=api_key,
            api_secret=api_secret,
        )

    def ping(self):
        return self._client.ping()

    def server_time(self):
        return self._client.time()

    def exchange_info(self):
        return self._client.exchange_info()

    def symbols(self) -> list[str]:
        markets = self.exchange_info()
        return [item["symbol"] for item in markets]

    def find_symbol(self, symbol: str):

        for market in self.exchange_info():
            if market["symbol"] == symbol:
                return market

        return None

    def trades(self, symbol: str, limit: int | None = None):

        data = self._client.trades(
            symbol=symbol,
            limit=limit,
        )

        return [Trade.from_api(item) for item in data]

    def depth(self, symbol: str, limit: int | None = None):

        data = self._client.depth(
            symbol=symbol,
            limit=limit,
        )

        return OrderBook.from_api(data)