"""تست Paper Trading."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from core.paper_trading import PaperLedger


class TestPaper(unittest.TestCase):
    def test_open_and_win(self):
        with tempfile.TemporaryDirectory() as d:
            ledger = PaperLedger(path=str(Path(d) / "paper.json"))
            t = ledger.open_trade("BTC/USDT", "BUY", 100.0, 95.0, 110.0, "test")
            self.assertEqual(t.status, "OPEN")
            ledger.update_price(t.id, 105.0)
            self.assertEqual(t.status, "OPEN")
            ledger.update_price(t.id, 111.0)
            self.assertEqual(t.status, "WIN")
            self.assertGreater(t.pnl_pct or 0, 0)
            perf = ledger.performance()
            self.assertEqual(perf["trades"], 1)
            self.assertEqual(perf["win_rate"], 100.0)

    def test_stop_loss(self):
        with tempfile.TemporaryDirectory() as d:
            ledger = PaperLedger(path=str(Path(d) / "paper.json"))
            t = ledger.open_trade("ETH/USDT", "BUY", 100.0, 95.0, 120.0)
            ledger.update_price(t.id, 94.0)
            self.assertEqual(t.status, "LOSS")


if __name__ == "__main__":
    unittest.main()
