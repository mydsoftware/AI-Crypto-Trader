"""لایه اتصال به صرافی‌ها — فقط داده عمومی، بدون ارسال سفارش."""
from .adapters import (
    ADAPTERS,
    BinanceAdapter,
    BybitAdapter,
    ExchangeAdapter,
    KrakenAdapter,
    OHLCV,
    OKXAdapter,
    OrderBookLevel,
    OrderBookSnapshot,
    TickerData,
    get_adapter,
)

__all__ = [
    "ADAPTERS",
    "BinanceAdapter",
    "BybitAdapter",
    "ExchangeAdapter",
    "KrakenAdapter",
    "OHLCV",
    "OKXAdapter",
    "OrderBookLevel",
    "OrderBookSnapshot",
    "TickerData",
    "get_adapter",
]
