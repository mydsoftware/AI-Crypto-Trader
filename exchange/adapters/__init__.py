"""
آداپترهای صرافی — فقط داده عمومی بازار.

ExchangeAdapter
    ├── BinanceAdapter
    ├── BybitAdapter
    ├── OKXAdapter
    └── KrakenAdapter
"""
from .base import (
    ExchangeAdapter,
    OHLCV,
    OrderBookLevel,
    OrderBookSnapshot,
    TickerData,
)
from .binance import BinanceAdapter
from .bybit import BybitAdapter
from .okx import OKXAdapter
from .kraken import KrakenAdapter

ADAPTERS: dict[str, type[ExchangeAdapter]] = {
    "binance": BinanceAdapter,
    "bybit": BybitAdapter,
    "okx": OKXAdapter,
    "kraken": KrakenAdapter,
}


def get_adapter(name: str = "binance", **kwargs) -> ExchangeAdapter:
    """ساخت آداپتر بر اساس نام."""
    cls = ADAPTERS.get(name.lower())
    if cls is None:
        raise ValueError(f"صرافی پشتیبانی‌نشده: {name}. گزینه‌ها: {list(ADAPTERS)}")
    return cls(**kwargs)


__all__ = [
    "ExchangeAdapter",
    "TickerData",
    "OHLCV",
    "OrderBookLevel",
    "OrderBookSnapshot",
    "BinanceAdapter",
    "BybitAdapter",
    "OKXAdapter",
    "KrakenAdapter",
    "ADAPTERS",
    "get_adapter",
]
