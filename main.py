"""
PACT-OS
Main Entry Point
"""

from analysis.ema import calculate as ema
from analysis.rsi import calculate as rsi
from analysis.macd import calculate as macd

from config import COLLECTOR_MODE

from database.database import Database

from exchange.tabdeal_client import TabdealClient

from market.collector import run_collector
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


def print_analysis(database: Database) -> None:

    prices = database.last_prices("BTCIRT", limit=100)

    # MACD حداقل به 35 قیمت نیاز دارد
    if len(prices) < 35:
        print("\nNot enough historical data.")
        return

    ema9 = ema(prices, 9)
    ema21 = ema(prices, 21)

    rsi14 = rsi(prices, 14)

    macd_result = macd(prices)

    print("\n" + "=" * 70)
    print("BTCIRT ANALYSIS")
    print("=" * 70)

    # =========================
    # EMA
    # =========================

    print(f"EMA(9)  : {ema9:,.0f}")
    print(f"EMA(21) : {ema21:,.0f}")

    if ema9 > ema21:
        trend = "BULLISH 📈"
    elif ema9 < ema21:
        trend = "BEARISH 📉"
    else:
        trend = "SIDEWAYS ➖"

    print(f"Trend   : {trend}")

    print()

    # =========================
    # RSI
    # =========================

    print(f"RSI(14) : {rsi14:.2f}")

    if rsi14 >= 70:
        rsi_signal = "OVERBOUGHT 🔴"
    elif rsi14 <= 30:
        rsi_signal = "OVERSOLD 🟢"
    else:
        rsi_signal = "NEUTRAL 🟡"

    print(f"RSI     : {rsi_signal}")

    print()

    # =========================
    # MACD
    # =========================

    print(f"MACD    : {macd_result['macd']:,.2f}")
    print(f"Signal  : {macd_result['signal']:,.2f}")
    print(f"Hist    : {macd_result['histogram']:,.2f}")

    if macd_result["macd"] > macd_result["signal"]:
        macd_signal = "BUY 🟢"
    elif macd_result["macd"] < macd_result["signal"]:
        macd_signal = "SELL 🔴"
    else:
        macd_signal = "HOLD 🟡"

    print(f"MACD    : {macd_signal}")


def run_once() -> None:

    client = TabdealClient()

    scanner = MarketScanner(client)

    database = Database()

    tickers = scanner.scan()

    database.save_markets(tickers)

    print(f"\nMarkets : {len(tickers)}")

    for ticker in tickers:
        print_ticker(ticker)

    print_analysis(database)


def main() -> None:

    banner()

    if COLLECTOR_MODE:
        run_collector()
    else:
        run_once()

    print("\n" + "=" * 70)
    print("PACT-OS READY")
    print("=" * 70)


if __name__ == "__main__":
    main()