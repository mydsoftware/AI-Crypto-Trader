"""موتور تصمیم‌گیری دستیار معامله‌گر؛ بدون اجرای سفارش."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Decision:
    action: str
    allowed: bool
    reason: str


class DecisionEngine:
    """سیگنال تحلیل را به تصمیم پیشنهادی برای کاربر تبدیل می‌کند."""

    def decide(self, signal: str) -> Decision:
        normalized = str(signal).strip().upper()

        if normalized == "STRONG BUY":
            return Decision("BUY", True, "سیگنال صعودی بسیار قوی است.")
        if normalized == "BUY":
            return Decision("BUY", True, "سیگنال صعودی است.")
        if normalized == "STRONG SELL":
            return Decision("SELL", True, "سیگنال نزولی بسیار قوی است.")
        if normalized == "SELL":
            return Decision("SELL", True, "سیگنال نزولی است.")

        return Decision("HOLD", False, "فرصت معاملاتی معتبر شناسایی نشد؛ فعلاً صبر کن.")
