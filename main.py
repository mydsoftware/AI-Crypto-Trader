"""
PACT-OS
Main Entry Point
"""

from analysis.analysis_engine import AnalysisEngine

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


def print_analysis(result) -> None:

    if result is None:

        print("-" * 70)
        print("Not enough historical data.")
        return

    print("-" * 70)

    print(f"EMA Signal   : {result.ema_signal}")
    print(f"RSI Signal   : {result.rsi_signal}")
    print(f"MACD Signal  : {result.macd_signal}")

    print()

    print(f"EMA(9)       : {result.ema9:,.2f}")
    print(f"EMA(21)      : {result.ema21:,.2f}")

    print(f"RSI(14)      : {result.rsi:.2f}")

    print(f"MACD         : {result.macd:.2f}")
    print(f"Signal Line  : {result.signal_line:.2f}")
    print(f"Histogram    : {result.histogram:.2f}")

    print()

    print(f"Score        : {result.score}")
    print(f"Final Signal : {result.signal}")


def run() -> None:

    client = TabdealClient()

    scanner = MarketScanner(client)

    database = Database()

    engine = AnalysisEngine(database)

    tickers = scanner.scan()

    database.save_markets(tickers)

    print(f"\nMarkets : {len(tickers)}")

    print()
    print("=" * 70)
    print("MARKET OVERVIEW")
    print("=" * 70)

    for ticker in tickers:
        print_ticker(ticker)

    print()
    print("=" * 70)
    print("TECHNICAL ANALYSIS")
    print("=" * 70)

    for ticker in tickers:

        print(f"\n{ticker.symbol}")

        result = engine.analyze(ticker.symbol)

        print_analysis(result)


def main() -> None:

    banner()

    run()

    print()
    print("=" * 70)
    print("PACT-OS READY")
    print("=" * 70)


if __name__ == "__main__":
    main()