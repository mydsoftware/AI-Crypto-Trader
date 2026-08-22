"""محافظ اجرای معامله؛ در حالت دستیار هیچ سفارشی ارسال نمی‌شود."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExecutionResult:
    executed: bool
    action: str
    message: str


class TradeExecutor:
    """اجرای سفارش عمداً غیرفعال است تا PACT-OS فقط دستیار معامله‌گری باشد."""

    def execute(self, action: str) -> ExecutionResult:
        action = str(action).upper()
        return ExecutionResult(
            executed=False,
            action=action if action in {"BUY", "SELL"} else "HOLD",
            message="حالت دستیار فعال است؛ هیچ سفارش واقعی یا شبیه‌سازی‌شده‌ای اجرا نشد.",
        )
