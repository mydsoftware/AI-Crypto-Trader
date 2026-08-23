"""
آداپتر Bybit — endpointهای عمومی REST اسپات.

بدون API Key برای داده بازار.
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
    "1m": "1",
    "5m": "5",
    "15m": "15",
    "1h": "60",
    "4h": "240",
    "1d": "D",
}


class BybitAdapter(ExchangeAdapter):
    name = "bybit"
    base_url = "https://api.bybit.com"

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
                data = json.loads(resp.read().decode("utf-8"))
            if data.get("retCode") not in (0, None) and data.get("ret_code") not in (0, None):
                raise RuntimeError(f"Bybit error: {data.get('retMsg') or data}")
            return data.get("result") or data
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Bybit request failed: {exc}") from exc

    def fetch_tickers(self, quote: str = "USDT") -> list[TickerData]:
        payload = self._get("/v5/market/tickers", {"category": "spot"})
        items = payload.get("list") or []
        result: list[TickerData] = []
        quote = quote.upper()
        for item in items:
            try:
                symbol = str(item["symbol"])
                if not symbol.endswith(quote):
                    continue
                result.append(
                    TickerData(
                        symbol=self.to_standard_symbol(symbol),
                        last_price=float(item.get("lastPrice") or 0),
                        bid=float(item.get("bid1Price") or 0) or None,
                        ask=float(item.get("ask1Price") or 0) or None,
                        volume_24h=float(item.get("volume24h") or 0),
                        quote_volume_24h=float(item.get("turnover24h") or 0),
                        price_change_pct_24h=float(item.get("price24hPcnt") or 0) * 100,
                        high_24h=float(item.get("highPrice24h") or 0) or None,
                        low_24h=float(item.get("lowPrice24h") or 0) or None,
                        exchange=self.name,
                        timestamp=int(time.time() * 1000),
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
        interval = _TF_MAP.get(timeframe, "60")
        raw = self.normalize_symbol(symbol)
        payload = self._get(
            "/v5/market/kline",
            {
                "category": "spot",
                "symbol": raw,
                "interval": interval,
                "limit": min(limit, 1000),
            },
        )
        rows = payload.get("list") or []
        candles: list[OHLCV] = []
        for row in reversed(rows):
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
        raw = self.normalize_symbol(symbol)
        payload = self._get(
            "/v5/market/orderbook",
            {"category": "spot", "symbol": raw, "limit": min(limit, 50)},
        )
        bids = [OrderBookLevel(float(p), float(q)) for p, q in payload.get("b", [])]
        asks = [OrderBookLevel(float(p), float(q)) for p, q in payload.get("a", [])]
        return OrderBookSnapshot(
            symbol=self.to_standard_symbol(raw),
            bids=bids,
            asks=asks,
            timestamp=int(payload.get("ts") or time.time() * 1000),
            exchange=self.name,
        )
