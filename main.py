"""
PACT-OS
Main Entry Point
"""

from analysis.analysis_engine import AnalysisEngine
from analysis.confidence import ConfidenceEngine
from analysis.explanation import ExplanationEngine
from analysis.market_trend import MarketTrendEngine
from analysis.mtf import (
    MTFEngine,
    TimeframeSignal,
)

from database.database import Database
from database.repository import CandleRepository

from decision.decision_engine import DecisionEngine

from exchange.tabdeal_client import TabdealClient

from journal.trade_journal import TradeJournal

from market.scanner import MarketScanner

from portfolio.portfolio import Portfolio

from risk.risk_manager import RiskManager


def banner() -> None:

    print("=" * 70)
    print("                 PACT-OS")
    print("      Personal AI Crypto Trading Assistant")
    print("=" * 70)


def print_market_trend(trend) -> None:

    print()
    print("=" * 70)
    print("MARKET TREND")
    print("=" * 70)

    print(f"Trend        : {trend.trend}")
    print(f"Strength     : {trend.strength}%")

    print()


def print_ticker(ticker) -> None:

    print(f"\n{ticker.symbol}")
    print("-" * 40)
    print(f"Last Price : {ticker.last_price:,.0f}")
    print(f"Best Bid   : {ticker.best_bid:,.0f}")
    print(f"Best Ask   : {ticker.best_ask:,.0f}")
    print(f"Spread     : {ticker.spread:,.0f}")
    print(f"Spread %   : {ticker.spread_percent:.4f}")


def print_portfolio(portfolio: Portfolio) -> None:

    print()
    print("=" * 70)
    print("PORTFOLIO")
    print("=" * 70)

    print(f"Cash      : {portfolio.cash:,.2f}")
    print(f"Positions : {len(portfolio.positions)}")


def print_risk(risk: RiskManager) -> None:

    print()
    print("=" * 70)
    print("RISK MANAGEMENT")
    print("=" * 70)

    print(f"Max Risk / Trade : {risk.max_risk_percent:.2f}%")
    print(f"Max Positions    : {risk.max_open_positions}")


def print_analysis(
    result,
    ticker,
    journal: TradeJournal,
) -> None:

    if result is None:

        print("-" * 70)
        print("Not enough historical data.")
        return

    confidence = ConfidenceEngine().evaluate(
        result.score
    )

    explanation = ExplanationEngine().explain(
        result
    )

    mtf = MTFEngine().evaluate(
        [
            TimeframeSignal("5m", result.signal),
            TimeframeSignal("15m", result.signal),
            TimeframeSignal("1h", result.signal),
            TimeframeSignal("4h", result.signal),
        ]
    )

    decision = DecisionEngine().decide(
        mtf.overall
    )

    journal.add(
        symbol=ticker.symbol,
        action=decision.action,
        quantity=0.0,
        price=ticker.last_price,
        status="ANALYSIS",
    )

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

    print()

    print("CONFIDENCE")
    print(f"Score        : {confidence.score}%")
    print(f"Level        : {confidence.level}")

    print()

    print("MTF ANALYSIS")

    for item in mtf.signals:
        print(f"{item.timeframe:<4} -> {item.signal}")

    print()

    print(f"Agreement    : {mtf.agreement * 100:.0f}%")
    print(f"Overall      : {mtf.overall}")

    print()

    print("EXPLANATION")
    print(f"Summary      : {explanation.summary}")

    print()

    print("Reasons")

    for reason in explanation.reasons:
        print(f"  ✓ {reason}")

    print()

    print("DECISION")
    print(f"Action       : {decision.action}")
    print(f"Allowed      : {decision.allowed}")
    print(f"Reason       : {decision.reason}")


def print_journal(
    journal: TradeJournal,
) -> None:

    print()
    print("=" * 70)
    print("TRADE JOURNAL")
    print("=" * 70)

    print(f"Total Records : {journal.total_trades}")


def run() -> None:

    client = TabdealClient()

    scanner = MarketScanner(client)

    database = Database()

    repository = CandleRepository(database)

    engine = AnalysisEngine(repository)

    portfolio = Portfolio()

    risk = RiskManager()

    journal = TradeJournal()

    tickers = scanner.scan()

    database.save_markets(tickers)

    analysis_results = {}

    market_signals = []

    for ticker in tickers:

        result = engine.analyze(
            ticker.symbol,
        )

        analysis_results[ticker.symbol] = result

        if result is not None:
            market_signals.append(result.signal)

    market_trend = MarketTrendEngine().evaluate(
        market_signals
    )

    print_market_trend(
        market_trend
    )

    print(f"Markets : {len(tickers)}")

    print()
    print("=" * 70)
    print("MARKET OVERVIEW")
    print("=" * 70)

    for ticker in tickers:
        print_ticker(ticker)

    print_portfolio(portfolio)

    print_risk(risk)

    print()
    print("=" * 70)
    print("TECHNICAL ANALYSIS")
    print("=" * 70)

    for ticker in tickers:

        print(f"\n{ticker.symbol}")

        print_analysis(
            analysis_results.get(
                ticker.symbol
            ),
            ticker,
            journal,
        )

    print_journal(journal)


def main() -> None:

    banner()

    run()

    print()
    print("=" * 70)
    print("PACT-OS READY")
    print("=" * 70)


if __name__ == "__main__":
    main()