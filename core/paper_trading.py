"""
Paper Trading — ثبت مجازی سیگنال و نتیجه.

قبل از هر Auto Trading واقعی.
AUTO_TRADING همچنان OFF است؛ این فقط شبیه‌سازی است.
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PaperTrade:
    id: str
    timestamp: float
    symbol: str
    direction: str
    entry: float
    stop_loss: float | None
    take_profit: float | None
    strategy: str
    status: str = "OPEN"
    exit_price: float | None = None
    pnl_pct: float | None = None
    mfe: float | None = None
    mae: float | None = None
    notes: str = ""


@dataclass
class PaperLedger:
    trades: list[PaperTrade] = field(default_factory=list)
    path: str = "data/paper_trades.json"

    def open_trade(
        self,
        symbol: str,
        direction: str,
        entry: float,
        stop_loss: float | None,
        take_profit: float | None,
        strategy: str = "ensemble",
        notes: str = "",
    ) -> PaperTrade:
        t = PaperTrade(
            id=f"{symbol}-{int(time.time()*1000)}",
            timestamp=time.time(),
            symbol=symbol,
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            strategy=strategy,
            notes=notes,
        )
        self.trades.append(t)
        self._save()
        return t

    def update_price(self, trade_id: str, price: float) -> PaperTrade | None:
        trade = next((t for t in self.trades if t.id == trade_id), None)
        if not trade or trade.status != "OPEN":
            return trade
        if trade.direction == "BUY":
            fav = (price - trade.entry) / trade.entry * 100
            adv = (trade.entry - price) / trade.entry * 100
        else:
            fav = (trade.entry - price) / trade.entry * 100
            adv = (price - trade.entry) / trade.entry * 100
        trade.mfe = max(trade.mfe or 0, fav)
        trade.mae = max(trade.mae or 0, adv)

        if trade.direction == "BUY":
            if trade.stop_loss and price <= trade.stop_loss:
                self._close(trade, price, "LOSS")
            elif trade.take_profit and price >= trade.take_profit:
                self._close(trade, price, "WIN")
        else:
            if trade.stop_loss and price >= trade.stop_loss:
                self._close(trade, price, "LOSS")
            elif trade.take_profit and price <= trade.take_profit:
                self._close(trade, price, "WIN")
        self._save()
        return trade

    def _close(self, trade: PaperTrade, price: float, status: str) -> None:
        trade.exit_price = price
        trade.status = status
        if trade.direction == "BUY":
            trade.pnl_pct = (price - trade.entry) / trade.entry * 100
        else:
            trade.pnl_pct = (trade.entry - price) / trade.entry * 100

    def performance(self) -> dict[str, Any]:
        closed = [t for t in self.trades if t.status in ("WIN", "LOSS", "CLOSED")]
        if not closed:
            return {"trades": 0, "win_rate": 0, "net_pnl_pct": 0, "avg_win": 0, "avg_loss": 0}
        wins = [t for t in closed if (t.pnl_pct or 0) > 0]
        losses = [t for t in closed if (t.pnl_pct or 0) <= 0]
        net = sum(t.pnl_pct or 0 for t in closed)
        return {
            "trades": len(closed),
            "open": sum(1 for t in self.trades if t.status == "OPEN"),
            "win_rate": round(len(wins) / len(closed) * 100, 1) if closed else 0,
            "net_pnl_pct": round(net, 2),
            "avg_win": round(sum(t.pnl_pct or 0 for t in wins) / len(wins), 2) if wins else 0,
            "avg_loss": round(sum(t.pnl_pct or 0 for t in losses) / len(losses), 2) if losses else 0,
        }

    def _save(self) -> None:
        p = Path(self.path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps([asdict(t) for t in self.trades], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load(self) -> None:
        p = Path(self.path)
        if not p.exists():
            return
        data = json.loads(p.read_text(encoding="utf-8"))
        self.trades = [PaperTrade(**row) for row in data]
