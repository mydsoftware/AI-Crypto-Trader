"""دستیار شخصی معامله‌گری؛ فقط تحلیل و پیشنهاد، بدون اجرای سفارش."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class TradePlan:
    symbol: str
    action: str
    confidence: float
    entry: float | None
    stop_loss: float | None
    take_profit_1: float | None
    take_profit_2: float | None
    risk_reward: float | None
    risk_percent: float
    allowed: bool
    reason: str
    warnings: list[str]


class TradingAssistant:
    """تحلیل نتیجه موجود را به یک برنامه معاملاتی قابل بررسی توسط کاربر تبدیل می‌کند."""

    def __init__(self, risk_percent: float = 1.0, min_confidence: float = 60.0) -> None:
        self.risk_percent = max(0.0, float(risk_percent))
        self.min_confidence = max(0.0, min(100.0, float(min_confidence)))

    @staticmethod
    def _number(result: Any, name: str) -> float | None:
        value = getattr(result, name, None)
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    def build_plan(self, symbol: str, result: Any, confidence: Any, decision: Any) -> TradePlan:
        score = self._number(confidence, "score") or 0.0
        action = str(getattr(decision, "action", "HOLD")).upper()
        allowed = bool(getattr(decision, "allowed", False))
        entry = self._number(result, "last_price") or self._number(result, "close")
        support = self._number(result, "support")
        resistance = self._number(result, "resistance")

        signal = str(getattr(result, "signal", "HOLD")).upper()
        if action not in {"BUY", "SELL"} or signal not in {"BUY", "SELL", "LONG", "SHORT"}:
            action = "HOLD"
            allowed = False

        warnings: list[str] = []
        if score < self.min_confidence:
            allowed = False
            warnings.append("اعتماد تحلیل پایین‌تر از حداقل تعیین‌شده است.")
        if entry is None:
            allowed = False
            warnings.append("قیمت ورود از داده تحلیل قابل استخراج نیست.")

        stop_loss = None
        take_profit_1 = None
        take_profit_2 = None
        risk_reward = None

        if entry is not None and action == "BUY":
            stop_loss = support
            take_profit_1 = resistance
            if stop_loss is not None and take_profit_1 is not None and entry > stop_loss:
                risk = entry - stop_loss
                reward = take_profit_1 - entry
                risk_reward = reward / risk if risk > 0 else None
                take_profit_2 = entry + (2 * risk)
        elif entry is not None and action == "SELL":
            stop_loss = resistance
            take_profit_1 = support
            if stop_loss is not None and take_profit_1 is not None and stop_loss > entry:
                risk = stop_loss - entry
                reward = entry - take_profit_1
                risk_reward = reward / risk if risk > 0 else None
                take_profit_2 = entry - (2 * risk)

        if risk_reward is not None and risk_reward < 1.5:
            allowed = False
            warnings.append("نسبت سود به زیان کمتر از 1:1.5 است.")

        reason = str(getattr(decision, "reason", "شرایط کافی برای ورود وجود ندارد."))
        if not allowed and not warnings:
            warnings.append("این پیشنهاد نیاز به بررسی بیشتر دارد و مجوز ورود ندارد.")

        return TradePlan(
            symbol=symbol,
            action=action,
            confidence=score,
            entry=entry,
            stop_loss=stop_loss,
            take_profit_1=take_profit_1,
            take_profit_2=take_profit_2,
            risk_reward=risk_reward,
            risk_percent=self.risk_percent,
            allowed=allowed,
            reason=reason,
            warnings=warnings,
        )

    @staticmethod
    def render(plan: TradePlan) -> str:
        def fmt(value: float | None) -> str:
            return "نامشخص" if value is None else f"{value:,.8f}"

        lines = [
            "\n" + "=" * 70,
            f"دستیار معامله‌گر | {plan.symbol}",
            "=" * 70,
            f"پیشنهاد       : {plan.action}",
            f"اعتماد        : {plan.confidence:.1f}%",
            f"ورود پیشنهادی : {fmt(plan.entry)}",
            f"حد ضرر        : {fmt(plan.stop_loss)}",
            f"هدف اول       : {fmt(plan.take_profit_1)}",
            f"هدف دوم       : {fmt(plan.take_profit_2)}",
            f"ریسک پیشنهادی : {plan.risk_percent:.2f}%",
            f"Risk/Reward   : {plan.risk_reward:.2f}" if plan.risk_reward is not None else "Risk/Reward   : نامشخص",
            f"وضعیت         : {'قابل بررسی برای ورود' if plan.allowed else 'عدم ورود / انتظار'}",
            f"دلیل          : {plan.reason}",
        ]
        if plan.warnings:
            lines.append("هشدارها:")
            lines.extend(f"  ⚠ {warning}" for warning in plan.warnings)
        lines.append("تصمیم نهایی و اجرای معامله: فقط توسط کاربر")
        return "\n".join(lines)
