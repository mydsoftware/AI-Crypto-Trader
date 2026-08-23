"""تست واحد ماژول پورصمدی و رژیم."""
from __future__ import annotations
import unittest
from exchange.adapters.base import OHLCV
from poursamadi import PoursamadiEngine, vote_pro_btb, vote_sp2l, vote_micromap
from core.regime import detect_regime
from core.technical import generate_technical_evidence, technical_score


def _candles(n: int = 80, start: float = 100.0, trend: float = 0.1) -> list[OHLCV]:
    out = []
    price = start
    for i in range(n):
        o = price
        c = price + trend
        h = max(o, c) + 0.5
        l = min(o, c) - 0.5
        out.append(OHLCV(i * 3600_000, o, h, l, c, 1000 + i))
        price = c
    return out


class TestPoursamadi(unittest.TestCase):
    def test_votes_structure(self):
        candles = _candles()
        eng = PoursamadiEngine()
        result = eng.analyze(candles)
        self.assertEqual(len(result.votes), 3)
        names = {v.name for v in result.votes}
        self.assertIn("Pro BTB", names)
        self.assertIn("SP2L", names)
        self.assertIn("MicroMAP", names)
        for v in result.votes:
            self.assertIn(v.direction, ("BUY", "SELL", "NEUTRAL"))
            self.assertGreaterEqual(v.score, 0)
            self.assertLessEqual(v.score, 100)

    def test_individual_votes(self):
        candles = _candles(100, trend=0.2)
        self.assertIsNotNone(vote_pro_btb(candles))
        self.assertIsNotNone(vote_sp2l(candles))
        self.assertIsNotNone(vote_micromap(candles))


class TestRegime(unittest.TestCase):
    def test_detect_bullish_trend(self):
        candles = _candles(120, start=50, trend=0.3)
        r = detect_regime(candles)
        self.assertIn(r.primary, ("Bull", "Bear", "Sideways"))
        self.assertIn(r.structure, ("Trending", "Ranging"))
        self.assertIn(r.volatility, ("High", "Low", "Normal"))
        self.assertTrue(r.strategy_weights)


class TestTechnical(unittest.TestCase):
    def test_evidence(self):
        candles = _candles(100)
        ev = generate_technical_evidence(candles)
        self.assertGreater(len(ev), 0)
        score, direction = technical_score(ev)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        self.assertIn(direction, ("BUY", "SELL", "NEUTRAL"))


if __name__ == "__main__":
    unittest.main()
