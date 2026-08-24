"""موتور داده بازار زنده و نرمال‌سازی داده صرافی‌ها."""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Iterable
from exchange.adapters import ExchangeAdapter, OHLCV, OrderBookSnapshot, TickerData, get_adapter

logger = logging.getLogger(__name__)

@dataclass
class MarketSnapshot:
    symbol: str
    price: float
    price_change_pct: float
    volume_24h: float
    quote_volume: float
    bid: float | None = None
    ask: float | None = None
    spread_pct: float | None = None
    liquidity_score: float = 50.0
    exchange: str = ""
    high_24h: float | None = None
    low_24h: float | None = None

class DataEngine:
    """دریافت داده عمومی بازار؛ تبدیل به‌صورت پیش‌فرض صرافی اصلی است."""
    def __init__(self, primary: str = "tabdeal", fallbacks: list[str] | None = None, quote: str = "IRT"):
        self.quote = quote.upper()
        self.primary_name = primary
        self.fallback_names = fallbacks if fallbacks is not None else ["okx", "binance"]
        self._adapters: dict[str, ExchangeAdapter] = {}
        self._load_adapters()

    def _load_adapters(self) -> None:
        for name in [self.primary_name] + self.fallback_names:
            try:
                self._adapters[name] = get_adapter(name)
            except Exception as exc:
                logger.warning("بارگذاری آداپتر %s ناموفق: %s", name, exc)

    def _ordered_adapters(self, exchange: str | None = None):
        if exchange and exchange in self._adapters:
            return [self._adapters[exchange]]
        return [self._adapters[n] for n in [self.primary_name] + self.fallback_names if n in self._adapters]

    @property
    def primary(self) -> ExchangeAdapter:
        if self.primary_name in self._adapters:
            return self._adapters[self.primary_name]
        if self._adapters:
            return next(iter(self._adapters.values()))
        raise RuntimeError("هیچ آداپتر صرافی در دسترس نیست.")

    def fetch_all_tickers(self) -> list[TickerData]:
        errors = []
        for adapter in self._ordered_adapters():
            try:
                tickers = adapter.fetch_tickers(self.quote)
                if tickers:
                    logger.info("تیکر از %s: %d نماد", adapter.name, len(tickers))
                    return tickers
            except Exception as exc:
                errors.append(f"{adapter.name}: {exc}")
        raise RuntimeError("دریافت تیکر ناموفق: " + "; ".join(errors))

    def fetch_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 200, exchange: str | None = None) -> list[OHLCV]:
        for adapter in self._ordered_adapters(exchange):
            try:
                candles = adapter.fetch_ohlcv(symbol, timeframe, limit)
                if candles:
                    return candles
            except Exception as exc:
                logger.warning("OHLCV %s/%s از %s: %s", symbol, timeframe, adapter.name, exc)
        return []

    def fetch_order_book(self, symbol: str, limit: int = 20, exchange: str | None = None) -> OrderBookSnapshot | None:
        for adapter in self._ordered_adapters(exchange):
            try:
                return adapter.fetch_order_book(symbol, limit)
            except Exception as exc:
                logger.warning("OrderBook %s از %s: %s", symbol, adapter.name, exc)
        return None

    def build_snapshots(self, min_quote_volume: float = 500_000, max_symbols: int = 150) -> list[MarketSnapshot]:
        tickers = sorted(self.fetch_all_tickers(), key=lambda t: t.quote_volume_24h, reverse=True)
        snapshots = []
        for t in tickers:
            if t.quote_volume_24h < min_quote_volume or len(snapshots) >= max_symbols:
                continue
            spread_pct = ((t.ask - t.bid) / t.bid * 100.0) if t.bid and t.ask and t.bid > 0 else None
            liq = min(100.0, max(10.0, (t.quote_volume_24h / 10_000_000) * 50))
            if spread_pct is not None and spread_pct > 0.5:
                liq *= 0.7
            snapshots.append(MarketSnapshot(t.symbol, t.last_price, t.price_change_pct_24h, t.volume_24h, t.quote_volume_24h, t.bid, t.ask, spread_pct, round(liq, 1), t.exchange, t.high_24h, t.low_24h))
        return snapshots

    def multi_timeframe_ohlcv(self, symbol: str, timeframes: Iterable[str] = ("5m", "15m", "1h", "4h", "1d"), limit: int = 120) -> dict[str, list[OHLCV]]:
        return {tf: candles for tf in timeframes if (candles := self.fetch_ohlcv(symbol, tf, limit))}
