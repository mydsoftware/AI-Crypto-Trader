"""دریافت داده عمومی بازار برای اسکن فرصت‌ها، بدون کلید و بدون ارسال سفارش."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.request import Request, urlopen
import json


@dataclass(slots=True)
class Ticker:
    symbol: str
    last_price: float
    price_change_pct: float
    quote_volume: float


def fetch_binance_tickers(base_url: str = "https://api.binance.com") -> list[Ticker]:
    """تیکرهای اسپات عمومی را از Binance دریافت می‌کند."""
    request = Request(f"{base_url.rstrip('/')}/api/v3/ticker/24hr", headers={"User-Agent": "AI-Crypto-Trader/1.0"})
    with urlopen(request, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))

    result: list[Ticker] = []
    for item in payload:
        try:
            symbol = str(item["symbol"])
            if not symbol.endswith("USDT"):
                continue
            result.append(
                Ticker(
                    symbol=symbol,
                    last_price=float(item["lastPrice"]),
                    price_change_pct=float(item["priceChangePercent"]),
                    quote_volume=float(item["quoteVolume"]),
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
    return result
