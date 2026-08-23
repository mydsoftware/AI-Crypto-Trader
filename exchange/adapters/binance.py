"""
آداپتر Binance — فقط endpointهای عمومی REST.

بدون نیاز به API Key برای داده بازار اسپات.
هیچ سفارشی ارسال نمی‌شود.
"""
from __future__ import annotations

from typing import Any

import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .base import (
    ExchangeAdapter,
    OHLCV,
    OrderBookLevel,
    OrderBookSnapshot,
    TickerData,
)

_TF_MAP = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
}


class BinanceAdapter(ExchangeAdapter):
    name = "binance"
    base_url = "https://api.binance.com"

    def __init__(self, base_url: str | None = None, timeout: int = 15):
        if base_url:
            self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, params: dict | None = None) -> Any:
        query = ""
        if params:
            query = "?" + "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{self.base_url}{path}{query}"
        req = Request(url, headers={"User-Agent": "AI-Crypto-Trader/1.0"})
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Binance request failed: {exc}") from exc

    def fetch_tickers(self, quote: str = "USDT") -> list[TickerData]:
        payload = self._get("/api/v3/ticker/24hr")
        result: list[TickerData] = []
        quote = quote.upper()
        for item in payload:
            try:
                symbol = str(item["symbol"])
                if not symbol.endswith(quote):
                    continue
                result.append(
                    TickerData(
                        symbol=self.to_standard_symbol(symbol),
                        last_price=float(item["lastPrice"]),
                        bid=float(item.get("bidPrice") or 0) or None,
                        ask=float(item.get("askPrice") or 0) or None,
                        volume_24h=float(item.get("volume") or 0),
                        quote_volume_24h=float(item.get("quoteVolume") or 0),
                        price_change_pct_24h=float(item.get("priceChangePercent") or 0),
                        high_24h=float(item.get("highPrice") or 0) or None,
                        low_24h=float(item.get("lowPrice") or 0) or None,
                        exchange=self.name,
                        timestamp=int(item.get("closeTime") or time.time() * 1000),
                    )
                )
            except (KeyError, TypeError, ValueError):
                continue
        return result

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 200,
    ) -> list[OHLCV]:
        interval = _TF_MAP.get(timeframe, "1h")
        raw_symbol = self.normalize_symbol(symbol)
        payload = self._get(
            "/api/v3/klines",
            {"symbol": raw_symbol, "interval": interval, "limit": min(limit, 1000)},
        )
        candles: list[OHLCV] = []
        for row in payload:
            try:
                candles.append(
                    OHLCV(
                        timestamp=int(row[0]),
                        open=float(row[1]),
                        high=float(row[2]),
                        low=float(row[3]),
                        close=float(row[4]),
                        volume=float(row[5]),
                    )
                )
            except (IndexError, TypeError, ValueError):
                continue
        return candles

    def fetch_order_book(self, symbol: str, limit: int = 20) -> OrderBookSnapshot:
        raw_symbol = self.normalize_symbol(symbol)
        payload = self._get(
            "/api/v3/depth",
            {"symbol": raw_symbol, "limit": min(limit, 100)},
        )
        bids = [
            OrderBookLevel(float(p), float(q))
            for p, q in payload.get("bids", [])
        ]
        asks = [
            OrderBookLevel(float(p), float(q))
            for p, q in payload.get("asks", [])
        ]
        return OrderBookSnapshot(
            symbol=self.to_standard_symbol(raw_symbol),
            bids=bids,
            asks=asks,
            timestamp=int(time.time() * 1000),
            exchange=self.name,
        )
