"""تست اختیاری اتصال زنده به API عمومی تبدیل."""
import os
import pytest
from exchange.adapters.tabdeal import TabdealAdapter

pytestmark = pytest.mark.integration

@pytest.mark.skipif(os.getenv("RUN_TABDEAL_LIVE") != "1", reason="تست زنده تبدیل با RUN_TABDEAL_LIVE=1 فعال می‌شود")
def test_tabdeal_public_market_data_live():
    adapter = TabdealAdapter()
    info = adapter.fetch_exchange_info()
    assert info
    tickers = adapter.fetch_tickers("IRT")
    assert tickers
    symbol = tickers[0].symbol
    candles = adapter.fetch_ohlcv(symbol, "1h", 10)
    assert candles
    book = adapter.fetch_order_book(symbol, 10)
    assert book is not None
    assert book.bids or book.asks
