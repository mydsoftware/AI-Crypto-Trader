"""
آداپتر Kraken — endpointهای عمومی REST.

توجه: نمادهای Kraken با XBT به جای BTC و فرمت خاص هستند.
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
    "1m": 1,
    "5m": 5,
    "15m": 15,
    "1h": 60,
    "4h": 240,
    "1d": 1440,
}

_SYMBOL_MAP = {
    "BTC/USDT": "XBTUSDT",
    "BTC/USD": "XBTUSD",
    "ETH/USDT": "ETHUSDT",
    "ETH/USD": "ETHUSD",
    "SOL/USDT": "SOLUSDT",
    "XRP/USDT": "XRPUSDT",
    "ADA/USDT": "ADAUSDT",
    "DOGE/USDT": "DOGEUSDT",
}


class KrakenAdapter(ExchangeAdapter):
    name = "kraken"
    base_url = "https://api.kraken.com"

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
            if data.get("error"):
                raise RuntimeError(f"Kraken error: {data['error']}")
            return data.get("result") or {}
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Kraken request failed: {exc}") from exc

    def normalize_symbol(self, symbol: str) -> str:
        s = symbol.upper().replace("/", "")
        if s.startswith("BTC"):
            s = "XBT" + s[3:]
        return _SYMBOL_MAP.get(symbol.upper(), s)

    def to_standard_symbol(self, exchange_symbol: str) -> str:
        s = exchange_symbol.upper()
        if s.startswith("XBT"):
            s = "BTC" + s[3:]
        for q in ("USDT", "USD", "EUR", "BTC", "ETH"):
            if s.endswith(q) and len(s) > len(q):
                return f"{s[:-len(q)]}/{q}"
        return s

    def fetch_tickers(self, quote: str = "USDT") -> list[TickerData]:
        pairs = self._get("/0/public/AssetPairs")
        symbols = []
        quote = quote.upper()
        for pair_name, info in pairs.items():
            wsname = info.get("wsname") or pair_name
            if quote in wsname or (quote == "USD" and "USD" in wsname and "USDT" not in wsname):
                symbols.append(pair_name)
        if not symbols:
            return []
        symbols = symbols[:80]
        payload = self._get("/0/public/Ticker", {"pair": ",".join(symbols)})
        result: list[TickerData] = []
        for pair, item in payload.items():
            try:
                last = float(item["c"][0])
                bid = float(item["b"][0])
                ask = float(item["a"][0])
                vol = float(item["v"][1])
                high = float(item["h"][1])
                low = float(item["l"][1])
                open_p = float(item["o"])
                change_pct = ((last - open_p) / open_p * 100) if open_p else 0.0
                result.append(
                    TickerData(
                        symbol=self.to_standard_symbol(pair),
                        last_price=last,
                        bid=bid,
                        ask=ask,
                        volume_24h=vol,
                        quote_volume_24h=0.0,
                        price_change_pct_24h=change_pct,
                        high_24h=high,
                        low_24h=low,
                        exchange=self.name,
                        timestamp=int(time.time() * 1000),
                    )
                )
            except (KeyError, TypeError, ValueError, IndexError):
                continue
        return result

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 200,
    ) -> list[OHLCV]:
        interval = _TF_MAP.get(timeframe, 60)
        pair = self.normalize_symbol(symbol)
        payload = self._get(
            "/0/public/OHLC",
            {"pair": pair, "interval": interval},
        )
        rows = []
        for key, val in payload.items():
            if key != "last" and isinstance(val, list):
                rows = val
                break
        candles: list[OHLCV] = []
        for row in rows[-limit:]:
            try:
                candles.append(
                    OHLCV(
                        timestamp=int(row[0]) * 1000,
                        open=float(row[1]),
                        high=float(row[2]),
                        low=float(row[3]),
                        close=float(row[4]),
                        volume=float(row[6]),
                    )
                )
            except (IndexError, TypeError, ValueError):
                continue
        return candles

    def fetch_order_book(self, symbol: str, limit: int = 20) -> OrderBookSnapshot:
        pair = self.normalize_symbol(symbol)
        payload = self._get(
            "/0/public/Depth",
            {"pair": pair, "count": min(limit, 50)},
        )
        data = {}
        for key, val in payload.items():
            if isinstance(val, dict):
                data = val
                break
        bids = [OrderBookLevel(float(p), float(q)) for p, q, *_ in data.get("bids", [])]
        asks = [OrderBookLevel(float(p), float(q)) for p, q, *_ in data.get("asks", [])]
        return OrderBookSnapshot(
            symbol=self.to_standard_symbol(pair),
            bids=bids,
            asks=asks,
            timestamp=int(time.time() * 1000),
            exchange=self.name,
        )
