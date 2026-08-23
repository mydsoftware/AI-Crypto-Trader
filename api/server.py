"""
API سرور ساده برای Dashboard و ChatGPT Integration.

endpointهای اصلی:
  GET /api/opportunities
  GET /api/market
  GET /api/health
  GET /api/analysis/{symbol}

بدون Auto Trading.
"""
from __future__ import annotations

import json
import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

_cache: dict = {"opportunities": None, "ts": 0}
CACHE_SECONDS = int(os.getenv("CACHE_SECONDS", "90"))


def get_engine():
    from core.opportunity_engine import OpportunityEngine
    return OpportunityEngine(
        min_quote_volume=float(os.getenv("MIN_QUOTE_VOLUME", "1000000")),
        max_symbols=int(os.getenv("MAX_SYMBOLS", "30")),
        min_score=float(os.getenv("MIN_SCORE", "50")),
    )


class Handler(BaseHTTPRequestHandler):
    def _json(self, data: dict, code: int = 200):
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        try:
            if path in ("/api/health", "/health"):
                self._json({"status": "ok", "auto_trading": False, "service": "AI-Crypto-Trader"})
                return

            if path in ("/api/opportunities", "/opportunities"):
                import time
                now = time.time()
                if _cache["opportunities"] and now - _cache["ts"] < CACHE_SECONDS:
                    self._json(_cache["opportunities"])
                    return
                eng = get_engine()
                opps = eng.scan()
                payload = eng.to_api_dict(opps)
                _cache["opportunities"] = payload
                _cache["ts"] = now
                self._json(payload)
                return

            if path in ("/api/market", "/market"):
                from core.data_engine import DataEngine
                de = DataEngine()
                snaps = de.build_snapshots(min_quote_volume=500_000, max_symbols=50)
                self._json({
                    "count": len(snaps),
                    "symbols": [
                        {
                            "symbol": s.symbol,
                            "price": s.price,
                            "changePct": s.price_change_pct,
                            "quoteVolume": s.quote_volume,
                            "liquidity": s.liquidity_score,
                            "spreadPct": s.spread_pct,
                            "exchange": s.exchange,
                        }
                        for s in snaps
                    ],
                })
                return

            if path.startswith("/api/analysis/") or path.startswith("/analysis/"):
                symbol = path.split("/")[-1].upper().replace("-", "/")
                if "/" not in symbol and symbol.endswith("USDT"):
                    symbol = symbol[:-4] + "/USDT"
                from core.data_engine import DataEngine
                from core.technical import generate_technical_evidence, technical_score
                de = DataEngine()
                candles = de.fetch_ohlcv(symbol, "1h", 120)
                if not candles:
                    self._json({"error": "داده یافت نشد", "symbol": symbol}, 404)
                    return
                evidences = generate_technical_evidence(candles)
                score, direction = technical_score(evidences)
                self._json({
                    "symbol": symbol,
                    "price": candles[-1].close,
                    "direction": direction,
                    "technicalScore": score,
                    "evidences": [
                        {"name": e.name, "direction": e.direction, "score": e.score, "reason": e.reason}
                        for e in evidences
                    ],
                })
                return

            self._json({"error": "مسیر نامعتبر", "path": path}, 404)
        except Exception as exc:
            logger.exception("API error")
            self._json({"error": str(exc), "live": False}, 500)

    def log_message(self, fmt, *args):
        logger.info("%s - %s", self.address_string(), fmt % args)


def main():
    port = int(os.getenv("PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    logger.info("API در حال اجرا روی پورت %s — AUTO_TRADING=OFF", port)
    server.serve_forever()


if __name__ == "__main__":
    main()
