"""
آداپتر صرافی تبدیل برای دریافت داده‌های عمومی بازار.

این ماژول فقط Market Data می‌گیرد و هیچ سفارشی ارسال نمی‌کند.
"""
from __future__ import annotations

import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from exchange.adapters import ExchangeAdapter, OHLCV, OrderBookSnapshot, TickerData


class TabdealAdapter(ExchangeAdapter):
    """آداپتر REST عمومی صرافی تبدیل."""

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
    def _normalize_symbol(symbol: str) -> str:
        symbol = symbol.upper()
        for quote in ("USDT", "IRT", "BTC", "ETH"):
            if symbol.endswith(quote) and len(symbol) > len(quote):
                return f"{symbol[:-len(quote)]}/{quote}"
        return symbol

    def fetch_exchange_info(self) -> dict:
        """اطلاعات نمادها و قوانین بازار را دریافت می‌کند."""
        return self._get("/exchangeInfo")

    def fetch_tickers(self, quote: str = "USDT") -> list[TickerData]:
        """تیکرهای بازار را دریافت و به مدل داخلی پروژه تبدیل می‌کند."""
        data = self._get("/ticker/24hr")
        rows = data if isinstance(data, list) else data.get("data", data.get("result", []))
        result: list[TickerData] = []
        quote = quote.upper()
        for row in rows:
            symbol = str(row.get("symbol", "")).upper()
            if not symbol.endswith(quote):
                continue
            last = float(row.get("lastPrice", row.get("last", 0)) or 0)
            if last <= 0:
                continue
            volume = float(row.get("volume", 0) or 0)
            quote_volume = float(row.get("quoteVolume", 0) or 0)
            change = float(row.get("priceChangePercent", 0) or 0)
            result.append(
                TickerData(
                    symbol=self._normalize_symbol(symbol),
                    last_price=last,
                    price_change_pct_24h=change,
                    volume_24h=volume,
                    quote_volume_24h=quote_volume,
                    bid=float(row.get("bidPrice", 0) or 0) or None,
                    ask=float(row.get("askPrice", 0) or 0) or None,
                    high_24h=float(row.get("highPrice", 0) or 0) or None,
                    low_24h=float(row.get("lowPrice", 0) or 0) or None,
                    exchange=self.name,
                )
            )
        return result

    def fetch_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 200) -> list[OHLCV]:
        """کندل‌های OHLCV را دریافت می‌کند."""
        interval_map = {"1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m", "1h": "1h", "2h": "2h", "4h": "4h", "6h": "6h", "8h": "8h", "12h": "12h", "1d": "1d", "3d": "3d", "1w": "1w"}
        interval = interval_map.get(timeframe, timeframe)
        raw = self._get("/klines", {"symbol": self._symbol(symbol), "interval": interval, "limit": min(limit, 1000)})
        rows = raw if isinstance(raw, list) else raw.get("data", raw.get("result", []))
        candles: list[OHLCV] = []
        for row in rows:
            if len(row) < 6:
                continue
            candles.append(
                OHLCV(
                    timestamp=int(row[0]) / 1000 if int(row[0]) > 10_000_000_000 else int(row[0]),
                    open=float(row[1]), high=float(row[2]), low=float(row[3]), close=float(row[4]), volume=float(row[5]),
                )
            )
        return candles[-limit:]

    def fetch_order_book(self, symbol: str, limit: int = 20) -> OrderBookSnapshot:
        """دفتر سفارشات واقعی تبدیل را دریافت می‌کند."""
        raw = self._get("/depth", {"symbol": self._symbol(symbol), "limit": min(limit, 1000)})
        data = raw.get("data", raw.get("result", raw)) if isinstance(raw, dict) else raw
        bids = [(float(x[0]), float(x[1])) for x in data.get("bids", [])]
        asks = [(float(x[0]), float(x[1])) for x in data.get("asks", [])]
        return OrderBookSnapshot(symbol=self._normalize_symbol(symbol), bids=bids, asks=asks, timestamp=time.time(), exchange=self.name)
