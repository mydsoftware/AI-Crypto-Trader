"""بک‌تست ساده و leakage-aware برای ارزیابی سیگنال‌های long-only."""
from __future__ import annotations
from dataclasses import dataclass
from .cost_model import CostModel

@dataclass(slots=True)
class BacktestResult:
    trades: int
    win_rate: float
    net_return: float
    max_drawdown: float
    profit_factor: float


def run_backtest(prices: list[float], signals: list[int], cost: CostModel | None = None) -> BacktestResult:
    if len(prices) != len(signals) or len(prices) < 2:
        raise ValueError("قیمت‌ها و سیگنال‌ها باید هم‌اندازه و معتبر باشند.")
    cost = cost or CostModel()
    equity = 1.0
    peak = equity
    max_dd = 0.0
    wins = losses = 0
    gross_profit = gross_loss = 0.0
    trades = 0
    position = 0
    entry = 0.0
    for i in range(1, len(prices)):
        signal = signals[i - 1]  # جلوگیری از استفاده از آینده
        if position == 0 and signal == 1:
            position = 1
            entry = prices[i]
            trades += 1
        elif position == 1 and signal <= 0:
            gross = prices[i] / entry - 1.0
            net = cost.net_return(gross)
            equity *= 1.0 + net
            if net > 0:
                wins += 1; gross_profit += net
            else:
                losses += 1; gross_loss += abs(net)
            position = 0
            peak = max(peak, equity)
            max_dd = max(max_dd, (peak - equity) / peak)
    if position == 1:
        net = cost.net_return(prices[-1] / entry - 1.0)
        equity *= 1.0 + net
        if net > 0: wins += 1; gross_profit += net
        else: losses += 1; gross_loss += abs(net)
        peak = max(peak, equity)
        max_dd = max(max_dd, (peak - equity) / peak)
    total = wins + losses
    return BacktestResult(trades, wins / total * 100 if total else 0.0, equity - 1.0, max_dd, gross_profit / gross_loss if gross_loss else float("inf"))
