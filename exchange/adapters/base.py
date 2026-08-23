"""
رابط پایه آداپتر صرافی‌ها.

این لایه فقط داده عمومی بازار را دریافت می‌کند و هیچ سفارشی ارسال نمی‌کند.
AUTO_TRADING همیشه خاموش است.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TickerData:
    """تیکر استاندارد بین صرافی‌ها."""
    symbol: str
    last_price: float
    bid: float | None = None
    ask: float | None = None
    volume_24h: float = 0.0
    quote_volume_24h: float = 0.0
    price_change_pct_24h: float = 0.0
    high_24h: float | None = None
    low_24h: float | None = None
    exchange: str = ""
    timestamp: int | None = None


@dataclass(slots=True)
class OHLCV:
    """کندل استاندارد OHLCV."""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(slots=True)
class OrderBookLevel:
    price: float
    quantity: float


@dataclass(slots=True)
class OrderBookSnapshot:
    """نمای لحظه‌ای دفتر سفارش."""
    symbol: str
    bids: list[OrderBookLevel] = field(default_factory=list)
    asks: list[OrderBookLevel] = field(default_factory=list)
    timestamp: int | None = None
    exchange: str = ""

    @property
    def best_bid(self) -> float | None:
        return self.bids[0].price if self.bids else None

    @property
    def best_ask(self) -> float | None:
        return self.asks[0].price if self.asks else None

    @property
    def spread(self) -> float | None:
        if self.best_bid is None or self.best_ask is None:
            return None
        return self.best_ask - self.best_bid

    @property
    def spread_pct(self) -> float | None:
        if self.best_bid is None or self.best_ask is None or self.best_bid <= 0:
            return None
        return (self.best_ask - self.best_bid) / self.best_bid * 100.0

    @property
    def mid_price(self) -> float | None:
        if self.best_bid is None or self.best_ask is None:
            return None
        return (self.best_bid + self.best_ask) / 2.0

    def imbalance(self, depth: int = 10) -> float | None:
        """نسبت فشار خرید به فروش در عمق مشخص (مثبت = فشار خرید)."""
        bid_vol = sum(l.quantity for l in self.bids[:depth])
        ask_vol = sum(l.quantity for l in self.asks[:depth])
        total = bid_vol + ask_vol
        if total <= 0:
            return None
        return (bid_vol - ask_vol) / total


class ExchangeAdapter(ABC):
    """رابط مشترک همه صرافی‌ها."""

    name: str = "base"
    # فقط endpointهای عمومی؛ هیچ کلید API در کد hard-code نمی‌شود.

    @abstractmethod
    def fetch_tickers(self, quote: str = "USDT") -> list[TickerData]:
        """لیست تیکرهای اسپات قابل معامله."""
        ...

    @abstractmethod
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 200,
    ) -> list[OHLCV]:
        """دریافت کندل‌های OHLCV."""
        ...

    @abstractmethod
    def fetch_order_book(self, symbol: str, limit: int = 20) -> OrderBookSnapshot:
        """دریافت دفتر سفارش."""
        ...

    def fetch_ticker(self, symbol: str) -> TickerData | None:
        """تیکر تک‌نماد (پیاده‌سازی پیش‌فرض روی fetch_tickers)."""
        for t in self.fetch_tickers():
            if t.symbol.upper() == symbol.upper():
                return t
        return None

    def normalize_symbol(self, symbol: str) -> str:
        """نرمال‌سازی نماد به فرمت داخلی صرافی."""
        return symbol.replace("/", "").upper()

    def to_standard_symbol(self, exchange_symbol: str) -> str:
        """تبدیل نماد صرافی به فرمت استاندارد BTC/USDT."""
        s = exchange_symbol.upper()
        for q in ("USDT", "USDC", "USD", "BTC", "ETH"):
            if s.endswith(q) and len(s) > len(q):
                return f"{s[:-len(q)]}/{q}"
        return s
