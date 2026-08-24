"""تست‌های واحد و اختیاری Integration برای آداپتر تبدیل."""
from __future__ import annotations
import os
import unittest
from unittest.mock import patch
from exchange.adapters.tabdeal import TabdealAdapter


class TestTabdealAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = TabdealAdapter()

    @patch.object(TabdealAdapter, "_get")
    def test_ticker_normalization(self, mock_get):
        mock_get.return_value = [{
            "symbol": "BTCIRT", "lastPrice": "100", "bidPrice": "99", "askPrice": "101",
            "volume": "10", "quoteVolume": "1000", "priceChangePercent": "2"
        }]
        rows = self.adapter.fetch_tickers("IRT")
        self.assertEqual(rows[0].symbol, "BTC/IRT")
        self.assertEqual(rows[0].exchange, "tabdeal")
        self.assertEqual(rows[0].last_price, 100.0)

    @patch.object(TabdealAdapter, "_get")
    def test_ohlcv(self, mock_get):
        mock_get.return_value = [[1700000000000, "1", "2", "0.5", "1.5", "20"]]
        candles = self.adapter.fetch_ohlcv("BTC/IRT", "1h", 10)
        self.assertEqual(len(candles), 1)
        self.assertEqual(candles[0].close, 1.5)

    @patch.object(TabdealAdapter, "_get")
    def test_order_book(self, mock_get):
        mock_get.return_value = {"bids": [["100", "2"]], "asks": [["101", "3"]]}
        book = self.adapter.fetch_order_book("BTCIRT", 10)
        self.assertEqual(book.bids[0].price, 100.0)
        self.assertEqual(book.asks[0].quantity, 3.0)

    @unittest.skipUnless(os.getenv("TABDEAL_LIVE_TEST") == "1", "برای تست شبکه‌ای TABDEAL_LIVE_TEST=1 تنظیم شود")
    def test_live_exchange_info(self):
        data = self.adapter.fetch_exchange_info()
        self.assertIsInstance(data, dict)
        self.assertTrue(data)

    @unittest.skipUnless(os.getenv("TABDEAL_LIVE_TEST") == "1", "برای تست شبکه‌ای TABDEAL_LIVE_TEST=1 تنظیم شود")
    def test_live_ticker(self):
        rows = self.adapter.fetch_tickers("IRT")
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 0)


if __name__ == "__main__":
    unittest.main()
