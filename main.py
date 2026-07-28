"""
PACT-OS
Main Entry Point
"""

from analysis.ema import calculate as ema
from analysis.macd import calculate as macd
from analysis.rsi import calculate as rsi
from analysis.signal_engine import evaluate

from config import HISTORY_LIMIT

from database.database import Database

from exchange.tabdeal_client import TabdealClient

from market.scanner import MarketScanner


def banner() -> None:

    print("=" * 70)
    print("                 PACT-OS")
    print("      Personal AI Crypto Trading Assistant")
    print("=" * 70)


def print_ticker(ticker) -> None:

    print(f"\n{ticker.symbol}")
    print("-" * 40)
    print(f"Last Price : {ticker.last_price:,.0f}")
    print(f"Best Bid   : {ticker.best_bid:,.0f}")
    print(f"Best Ask   : {ticker.best_ask:,.0f}")
    print(f"Spread     : {ticker.spread:,.0f}")
    print(f"Spread %   : {ticker.spread_percent:.4f}")


def analyze_symbol(database: Database, symbol: str) -> None:

    prices = database.last_prices(
        symbol,
        limit=HISTORY_LIMIT,
    )

    if len(prices) < 35:

        print(f"\n{symbol}")
        print("-" * 70)
        print("Not enough historical data.")
        return

    ema9 = ema(prices, 9)
    ema21 = ema(prices, 21)

    rsi14 = rsi(prices, 14)

    macd_result = macd(prices)

    result = evaluate(
        ema9=ema9,
        ema21=ema21,
        rsi14=rsi14,
        macd=macd_result["macd"],
        signal=macd_result["signal"],
    )

    print(f"\n{symbol}")
    print("-" * 70)

    print(f"EMA Signal   : {result['details']['ema']}")
    print(f"RSI Signal   : {result['details']['rsi']}")
    print(f"MACD Signal  : {result['details']['macd']}")

    print()

    print(f"EMA(9)       : {ema9:,.2f}")
    print(f"EMA(21)      : {ema21:,.2f}")

    print(f"RSI(14)      : {rsi14:.2f}")

    print(f"MACD         : {macd_result['macd']:.2f}")
    print(f"Signal Line  : {macd_result['signal']:.2f}")
    print(f"Histogram    : {macd_result['histogram']:.2f}")

    print()

    print(f"Score        : {result['score']}")
    print(f"Final Signal : {result['signal']}")


def run() -> None:

    client = TabdealClient()

    scanner = MarketScanner(client)

    database = Database()

    tickers = scanner.scan()

    database.save_markets(tickers)

    print(f"\nMarkets : {len(tickers)}")

    print("\n")
    print("=" * 70)
    print("MARKET OVERVIEW")
    print("=" * 70)

    for ticker in tickers:
        print_ticker(ticker)

    print("\n")
    print("=" * 70)
    print("TECHNICAL ANALYSIS")
    print("=" * 70)

    for ticker in tickers:

        analyze_symbol(
            database,
            ticker.symbol,
        )


def main() -> None:

    banner()

    run()

    print("\n")
    print("=" * 70)
    print("PACT-OS READY")
    print("=" * 70)


if __name__ == "__main__":
    main()