"""
PACT-OS
Market Collector
"""

from __future__ import annotations

import time

from database.database import Database
from exchange.tabdeal_client import TabdealClient
from market.scanner import MarketScanner
from config import SCAN_INTERVAL


def run_collector() -> None:

    client = TabdealClient()

    scanner = MarketScanner(client)

    database = Database()

    cycle = 1

    while True:

        print("\n" + "=" * 70)
        print(f"Cycle #{cycle}")
        print("=" * 70)

        try:

            tickers = scanner.scan()

            database.save_markets(tickers)

            print(f"Saved {len(tickers)} markets.")

        except Exception as exc:
            print(f"Error: {exc}")

        cycle += 1

        print(f"\nWaiting {SCAN_INTERVAL} seconds...\n")

        time.sleep(SCAN_INTERVAL)