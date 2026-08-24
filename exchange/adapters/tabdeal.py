"""آداپتر صرافی تبدیل برای دریافت داده عمومی بازار؛ بدون ارسال سفارش."""
from __future__ import annotations

import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .base import ExchangeAdapter, OHLCV, OrderBookLevel, OrderBookSnapshot, TickerData


class TabdealAdapter(ExchangeAdapter):
    """اتصال REST عمومی صرافی تبدیل."""

    name = "tabdeal"
    base_url = "https://api1.tabdeal.org/r/api/v1"

    def _get(self, path: str, params: dict | None = None):
        url = f"{self.base_url}{path}"
        if params:
            url += "?" + urlencode(params)
        request = Request(url, headers={"Accept": "application/json", "User-Agent": "AI-Crypto-Trader/1.0"})
        try:
            with urlopen(request, timeout=15) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RuntimeError(f"Tabdeal API error: {exc}") from exc

    @staticmethod
    def _symbol(symbol: str) -> str:
        return symbol.replace("/", "").replace("-", "").replace("_", "").upper()

    @staticmethod
    def _standard(symbol: str) -> str:
        s = symbol.upper()
        for quote in ("USDT", "IRT", "USDC", "BTC", "ETH"):
            if s.endswith(quote) and len(s) > len(quote):
                return f"{s[:-len(quote)]}/{quote}"
        return s

    @staticmethod
    def _rows(data):
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("data", data.get("result", []))
        return []

    def fetch_exchange_info(self) -> dict:
        return self._get("/exchangeInfo")

    def fetch_tickers(self, quote: str = "IRT") -> list[TickerData]:
        data = self._get("/ticker/24hr")
        result: list[TickerData] = []
        quote = quote.upper()
        for row in self._rows(data):
            symbol = str(row.get("symbol", "")).upper()
            if quote and not symbol.endswith(quote):
                continue
            last = float(row.get("lastPrice", row.get("last", 0)) or 0)
            if last <= 0:
                continue
            result.append(TickerData(
                symbol=self._standard(symbol),
                last_price=last,
                bid=float(row.get("bidPrice", 0) or 0) or None,
                ask=float(row.get("askPrice", 0) or 0) or None,
                volume_24h=float(row.get("volume", 0) or 0),
                quote_volume_24h=float(row.get("quoteVolume", 0) or 0),
                price_change_pct_24h=float(row.get("priceChangePercent", 0) or 0),
                high_24h=float(row.get("highPrice", 0) or 0) or None,
                low_24h=float(row.get("lowPrice", 0) or 0) or None,
                exchange=self.name,
                timestamp=int(time.time()),
            ))
        return result

    def fetch_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 200) -> list[OHLCV]:
        data = self._get("/klines", {"symbol": self._symbol(symbol), "interval": timeframe, "limit": min(limit, 1000)})
        candles: list[OHLCV] = []
        for row in self._rows(data):
            if len(row) < 6:
                continue
            ts = int(row[0])
            candles.append(OHLCV(
                timestamp=ts // 1000 if ts > 10_000_000_000 else ts,
                open=float(row[1]), high=float(row[2]), low=float(row[3]),
                close=float(row[4]), volume=float(row[5]),
            ))
        return candles[-limit:]

    def fetch_order_book(self, symbol: str, limit: int = 20) -> OrderBookSnapshot:
        raw = self._get("/depth", {"symbol": self._symbol(symbol), "limit": min(limit, 1000)})
        data = raw.get("data", raw.get("result", raw)) if isinstance(raw, dict) else raw
        bids = [OrderBookLevel(float(x[0]), float(x[1])) for x in data.get("bids", [])]
        asks = [OrderBookLevel(float(x[0]), float(x[1])) for x in data.get("asks", [])]
        return OrderBookSnapshot(
            symbol=self._standard(symbol), bids=bids, asks=asks,
            timestamp=int(time.time() * 1000), exchange=self.name,
        )
