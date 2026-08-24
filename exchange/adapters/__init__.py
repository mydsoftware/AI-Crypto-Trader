"""آداپترهای صرافی — فقط داده عمومی بازار."""
from .base import ExchangeAdapter, OHLCV, OrderBookLevel, OrderBookSnapshot, TickerData
from .binance import BinanceAdapter
from .bybit import BybitAdapter
from .okx import OKXAdapter
from .kraken import KrakenAdapter
from .tabdeal import TabdealAdapter

ADAPTERS: dict[str, type[ExchangeAdapter]] = {
    "tabdeal": TabdealAdapter,
    "binance": BinanceAdapter,
    "bybit": BybitAdapter,
    "okx": OKXAdapter,
    "kraken": KrakenAdapter,
}


def get_adapter(name: str = "tabdeal", **kwargs) -> ExchangeAdapter:
    """ساخت آداپتر بر اساس نام صرافی."""
    cls = ADAPTERS.get(name.lower())
    if cls is None:
        raise ValueError(f"صرافی پشتیبانی‌نشده: {name}. گزینه‌ها: {list(ADAPTERS)}")
    return cls(**kwargs)


__all__ = [
    "ExchangeAdapter", "TickerData", "OHLCV", "OrderBookLevel", "OrderBookSnapshot",
    "BinanceAdapter", "BybitAdapter", "OKXAdapter", "KrakenAdapter", "TabdealAdapter",
    "ADAPTERS", "get_adapter",
]
