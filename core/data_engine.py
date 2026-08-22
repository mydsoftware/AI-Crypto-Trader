"""
موتور داده بازار زنده.

از آداپترهای Multi-Exchange استفاده می‌کند.
فقط داده عمومی؛ بدون کلید API hard-coded و بدون ارسال سفارش.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Iterable

from exchange.adapters import (
    ExchangeAdapter,
    OHLCV,
    OrderBookSnapshot,
    TickerData,
    get_adapter,
)

logger = logging.getLogger(__name__)


@dataclass
class MarketSnapshot:
    """نمای خلاصه یک نماد برای اسکنر."""
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
    """
    موتور دریافت و نرمال‌سازی داده بازار از چندین صرافی.

    پیش‌فرض: OKX (قابل دسترس در محیط فعلی).
    در صورت خطا fallback به صرافی‌های دیگر انجام می‌شود.
    """

    def __init__(
        self,
        primary: str = "okx",
        fallbacks: list[str] | None = None,
        quote: str = "USDT",
    ):
        self.quote = quote.upper()
        self.primary_name = primary
        self.fallback_names = fallbacks or ["kraken", "binance"]
        self._adapters: dict[str, ExchangeAdapter] = {}
        self._load_adapters()

    def _load_adapters(self) -> None:
        for name in [self.primary_name] + self.fallback_names:
            try:
                self._adapters[name] = get_adapter(name)
            except Exception as exc:
                logger.warning("بارگذاری آداپتر %s ناموفق: %s", name, exc)

    @property
    def primary(self) -> ExchangeAdapter:
        if self.primary_name in self._adapters:
            return self._adapters[self.primary_name]
        if self._adapters:
            return next(iter(self._adapters.values()))
        raise RuntimeError("هیچ آداپتر صرافی در دسترس نیست.")

    def fetch_all_tickers(self) -> list[TickerData]:
        """تلاش با primary سپس fallback."""
        errors: list[str] = []
        for name, adapter in self._adapters.items():
            try:
                tickers = adapter.fetch_tickers(self.quote)
                if tickers:
                    logger.info("تیکر از %s: %d نماد", name, len(tickers))
                    return tickers
            except Exception as exc:
                errors.append(f"{name}: {exc}")
                logger.warning("fetch_tickers %s شکست: %s", name, exc)
        raise RuntimeError("دریافت تیکر از همه صرافی‌ها ناموفق بود: " + "; ".join(errors))

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 200,
        exchange: str | None = None,
    ) -> list[OHLCV]:
        adapters = (
            [self._adapters[exchange]]
            if exchange and exchange in self._adapters
            else list(self._adapters.values())
        )
        for adapter in adapters:
            try:
                candles = adapter.fetch_ohlcv(symbol, timeframe, limit)
                if candles:
                    return candles
            except Exception as exc:
                logger.warning("OHLCV %s/%s از %s: %s", symbol, timeframe, adapter.name, exc)
        return []

    def fetch_order_book(
        self,
        symbol: str,
        limit: int = 20,
        exchange: str | None = None,
    ) -> OrderBookSnapshot | None:
        adapters = (
            [self._adapters[exchange]]
            if exchange and exchange in self._adapters
            else list(self._adapters.values())
        )
        for adapter in adapters:
            try:
                return adapter.fetch_order_book(symbol, limit)
            except Exception as exc:
                logger.warning("OrderBook %s از %s: %s", symbol, adapter.name, exc)
        return None

    def build_snapshots(
        self,
        min_quote_volume: float = 500_000,
        max_symbols: int = 150,
    ) -> list[MarketSnapshot]:
        """
        ساخت لیست نمادهای قابل اسکن با فیلتر نقدشوندگی حداقلی.
        Discovery کامل بازار — محدود به لیست ثابت نیست.
        """
        tickers = self.fetch_all_tickers()
        tickers = sorted(tickers, key=lambda t: t.quote_volume_24h, reverse=True)
        snapshots: list[MarketSnapshot] = []
        for t in tickers:
            if t.quote_volume_24h < min_quote_volume:
                continue
            if len(snapshots) >= max_symbols:
                break
            spread_pct = None
            if t.bid and t.ask and t.bid > 0:
                spread_pct = (t.ask - t.bid) / t.bid * 100.0
            liq = min(100.0, max(10.0, (t.quote_volume_24h / 10_000_000) * 50))
            if spread_pct is not None and spread_pct > 0.5:
                liq *= 0.7
            snapshots.append(
                MarketSnapshot(
                    symbol=t.symbol,
                    price=t.last_price,
                    price_change_pct=t.price_change_pct_24h,
                    volume_24h=t.volume_24h,
                    quote_volume=t.quote_volume_24h,
                    bid=t.bid,
                    ask=t.ask,
                    spread_pct=spread_pct,
                    liquidity_score=round(liq, 1),
                    exchange=t.exchange,
                    high_24h=t.high_24h,
                    low_24h=t.low_24h,
                )
            )
        return snapshots

    def multi_timeframe_ohlcv(
        self,
        symbol: str,
        timeframes: Iterable[str] = ("5m", "15m", "1h", "4h", "1d"),
        limit: int = 120,
    ) -> dict[str, list[OHLCV]]:
        """دریافت کندل برای چند تایم‌فریم."""
        result: dict[str, list[OHLCV]] = {}
        for tf in timeframes:
            candles = self.fetch_ohlcv(symbol, tf, limit)
            if candles:
                result[tf] = candles
        return result
