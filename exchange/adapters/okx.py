"""
آداپتر OKX — endpointهای عمومی REST اسپات.
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
    "1h": "1H",
    "4h": "4H",
    "1d": "1D",
}


class OKXAdapter(ExchangeAdapter):
    name = "okx"
    base_url = "https://www.okx.com"

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
            if str(data.get("code")) not in ("0", "None"):
                raise RuntimeError(f"OKX error: {data.get('msg') or data}")
            return data.get("data") or []
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"OKX request failed: {exc}") from exc

    def normalize_symbol(self, symbol: str) -> str:
        # OKX از BTC-USDT استفاده می‌کند
        s = symbol.replace("/", "-").upper()
        if "-" not in s:
            for q in ("USDT", "USDC", "USD"):
                if s.endswith(q) and len(s) > len(q):
                    return f"{s[:-len(q)]}-{q}"
        return s

    def to_standard_symbol(self, exchange_symbol: str) -> str:
        return exchange_symbol.replace("-", "/").upper()

    def fetch_tickers(self, quote: str = "USDT") -> list[TickerData]:
        payload = self._get("/api/v5/market/tickers", {"instType": "SPOT"})
        result: list[TickerData] = []
        quote = quote.upper()
        for item in payload:
            try:
                inst = str(item.get("instId") or "")
                if not inst.endswith(f"-{quote}"):
                    continue
                result.append(
                    TickerData(
                        symbol=self.to_standard_symbol(inst),
                        last_price=float(item.get("last") or 0),
                        bid=float(item.get("bidPx") or 0) or None,
                        ask=float(item.get("askPx") or 0) or None,
                        volume_24h=float(item.get("vol24h") or 0),
                        quote_volume_24h=float(item.get("volCcy24h") or 0),
                        price_change_pct_24h=0.0,
                        high_24h=float(item.get("high24h") or 0) or None,
                        low_24h=float(item.get("low24h") or 0) or None,
                        exchange=self.name,
                        timestamp=int(item.get("ts") or time.time() * 1000),
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
        bar = _TF_MAP.get(timeframe, "1H")
        inst = self.normalize_symbol(symbol)
        payload = self._get(
            "/api/v5/market/candles",
            {"instId": inst, "bar": bar, "limit": str(min(limit, 300))},
        )
        candles: list[OHLCV] = []
        for row in reversed(payload):
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
        inst = self.normalize_symbol(symbol)
        payload = self._get(
            "/api/v5/market/books",
            {"instId": inst, "sz": str(min(limit, 50))},
        )
        data = payload[0] if payload else {}
        bids = [OrderBookLevel(float(p), float(q)) for p, q, *_ in data.get("bids", [])]
        asks = [OrderBookLevel(float(p), float(q)) for p, q, *_ in data.get("asks", [])]
        return OrderBookSnapshot(
            symbol=self.to_standard_symbol(inst),
            bids=bids,
            asks=asks,
            timestamp=int(data.get("ts") or time.time() * 1000),
            exchange=self.name,
        )
