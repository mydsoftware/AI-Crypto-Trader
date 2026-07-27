"""
PACT-OS
Main Entry Point
"""

from database.database import Database
from database.market_repository import MarketRepository
from exchange.tabdeal_client import TabdealClient
from market.scanner import MarketScanner


def banner() -> None:
    print("=" * 70)
    print("                 PACT-OS v0.1")
    print("       Personal AI Crypto Trading Assistant")
    print("=" * 70)


def print_ticker(ticker) -> None:
    print(f"\n{ticker.symbol}")
    print("-" * 40)
    print(f"Last Price : {ticker.last_price:,.0f}")
    print(f"Best Bid   : {ticker.best_bid:,.0f}")
    print(f"Best Ask   : {ticker.best_ask:,.0f}")
    print(f"Spread     : {ticker.spread:,.0f}")
    print(f"Spread %   : {ticker.spread_percent:.4f}")


def main() -> None:

    banner()

    client = TabdealClient()

    database = Database()
    session = database.session()

    repository = MarketRepository(session)

    scanner = MarketScanner(client)

    print("\nScanning market...")

    tickers = scanner.scan()

    repository.save_all(tickers)

    print(f"\nSaved {len(tickers)} market snapshots.")

    print("\n" + "=" * 70)

    for ticker in tickers:
        print_ticker(ticker)

    print("\n" + "=" * 70)
    print("PACT-OS READY")
    print("=" * 70)

    session.close()


if __name__ == "__main__":
    main()