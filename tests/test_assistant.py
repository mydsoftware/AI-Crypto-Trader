"""تست‌های هسته دستیار معامله‌گری."""

import unittest
from types import SimpleNamespace

from assistant import TradingAssistant


class TradingAssistantTests(unittest.TestCase):
    def test_hold_is_not_allowed(self):
        result = SimpleNamespace(signal="HOLD", support=90.0, resistance=110.0)
        confidence = SimpleNamespace(score=50, level="LOW")
        decision = SimpleNamespace(action="HOLD", allowed=False, reason="شرایط کافی نیست")
        plan = TradingAssistant().build_plan("BTCUSDT", result, confidence, decision, entry=100.0)
        self.assertEqual(plan.action, "HOLD")
        self.assertFalse(plan.allowed)

    def test_buy_plan_is_generated_without_execution(self):
        result = SimpleNamespace(signal="BUY", support=90.0, resistance=120.0)
        confidence = SimpleNamespace(score=85, level="HIGH")
        decision = SimpleNamespace(action="BUY", allowed=True, reason="تأیید")
        plan = TradingAssistant().build_plan("BTCUSDT", result, confidence, decision, entry=100.0)
        self.assertEqual(plan.action, "BUY")
        self.assertEqual(plan.entry, 100.0)
        self.assertEqual(plan.stop_loss, 90.0)
        self.assertEqual(plan.take_profit_1, 120.0)
        self.assertGreaterEqual(plan.risk_reward, 1.5)
        self.assertTrue(plan.allowed)


if __name__ == "__main__":
    unittest.main()
