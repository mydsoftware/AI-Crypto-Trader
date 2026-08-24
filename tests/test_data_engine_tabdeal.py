"""تست اتصال DataEngine به تبدیل بدون نیاز به شبکه."""
from __future__ import annotations
import unittest
from unittest.mock import patch
from core.data_engine import DataEngine
from exchange.adapters import TickerData


class TestDataEngineTabdeal(unittest.TestCase):
    @patch("core.data_engine.get_adapter")
    def test_tabdeal_is_primary_and_irt_is_default(self, get_adapter):
        class Fake:
            name = "tabdeal"
            def fetch_tickers(self, quote):
                self.quote = quote
                return [TickerData("BTC/IRT", 100, 1, 1000, 1000000, exchange="tabdeal")]
        fake = Fake()
        get_adapter.side_effect = lambda name: fake
        engine = DataEngine()
        rows = engine.fetch_all_tickers()
        self.assertEqual(engine.primary_name, "tabdeal")
        self.assertEqual(engine.quote, "IRT")
        self.assertEqual(fake.quote, "IRT")
        self.assertEqual(rows[0].exchange, "tabdeal")


if __name__ == "__main__":
    unittest.main()
