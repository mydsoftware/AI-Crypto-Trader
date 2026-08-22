"""ورودی اصلی PACT-OS؛ دستیار شخصی معامله‌گری بدون اجرای سفارش."""

from analysis.analysis_engine import AnalysisEngine
from analysis.confidence import ConfidenceEngine
from analysis.explanation import ExplanationEngine
from analysis.market_trend import MarketTrendEngine
from analysis.mtf import MTFEngine, TimeframeSignal
from analysis.ranking import RankingEngine, Opportunity
from assistant import TradingAssistant
from database.database import Database
from database.repository import CandleRepository
from decision.decision_engine import DecisionEngine
from exchange.tabdeal_client import TabdealClient
from journal.trade_journal import TradeJournal
from market.scanner import MarketScanner
from market.watchlist_engine import WatchlistEngine
from portfolio.portfolio import Portfolio
from risk.risk_manager import RiskManager
from config import WATCHLIST


def banner() -> None:
    print("=" * 70)
    print("                 PACT-OS")
    print("       Personal AI Crypto Trading Assistant")
    print("       حالت دستیار: بدون اجرای سفارش")
    print("=" * 70)


def print_watchlist(watchlist: WatchlistEngine) -> None:
    print("\n" + "=" * 70)
    print("WATCHLIST")
    print("=" * 70)
    print(f"Symbols : {watchlist.count}")
    for symbol in watchlist.all():
        print(f"  • {symbol}")


def print_ticker(ticker) -> None:
    print(f"\n{ticker.symbol}")
    print("-" * 40)
    print(f"Last Price : {ticker.last_price:,.8f}")
    print(f"Best Bid   : {ticker.best_bid:,.8f}")
    print(f"Best Ask   : {ticker.best_ask:,.8f}")
    print(f"Spread %   : {ticker.spread_percent:.4f}")


def analyze_symbol(ticker, result, journal, assistant) -> None:
    if result is None:
        print("داده تاریخی کافی نیست.")
        return

    confidence = ConfidenceEngine().evaluate(result.score)
    explanation = ExplanationEngine().explain(result)
    mtf = MTFEngine().evaluate([
        TimeframeSignal("5m", result.signal),
        TimeframeSignal("15m", result.signal),
        TimeframeSignal("1h", result.signal),
        TimeframeSignal("4h", result.signal),
    ])
    decision = DecisionEngine().decide(mtf.overall)

    plan = assistant.build_plan(ticker.symbol, result, confidence, decision)

    journal.add(
        symbol=ticker.symbol,
        action=decision.action,
        quantity=0.0,
        price=ticker.last_price,
        status="ASSISTANT_ANALYSIS",
    )

    print("\n" + "-" * 70)
    print("تحلیل تکنیکال")
    print(f"EMA Signal   : {result.ema_signal}")
    print(f"RSI Signal   : {result.rsi_signal}")
    print(f"MACD Signal  : {result.macd_signal}")
    print(f"EMA(9)       : {result.ema9:,.8f}")
    print(f"EMA(21)      : {result.ema21:,.8f}")
    print(f"RSI(14)      : {result.rsi:.2f}")
    print(f"Score        : {result.score}")
    print(f"Signal       : {result.signal}")
    print(f"Support      : {result.support:,.8f}")
    print(f"Resistance   : {result.resistance:,.8f}")
    print(f"Breakout     : {result.breakout_status}")
    print(f"Pullback     : {result.pullback_status}")
    print(f"Volume       : {result.volume_status}")
    print(f"Liquidity    : {result.liquidity_zone}")
    print(f"Order Flow   : {result.order_flow_signal}")

    print("\nCONFIDENCE / MTF")
    print(f"Confidence   : {confidence.score}% ({confidence.level})")
    print(f"MTF Agreement: {mtf.agreement * 100:.0f}%")
    print(f"MTF Overall  : {mtf.overall}")

    print("\nEXPLANATION")
    print(f"{explanation.summary}")
    for reason in explanation.reasons:
        print(f"  ✓ {reason}")

    print(TradingAssistant.render(plan))


def run() -> None:
    client = TabdealClient()
    watchlist = WatchlistEngine()
    watchlist.load(WATCHLIST)
    scanner = MarketScanner(client)
    database = Database()
    repository = CandleRepository(database)
    engine = AnalysisEngine(repository)
    portfolio = Portfolio()
    risk = RiskManager()
    journal = TradeJournal()
    ranking_engine = RankingEngine()
    assistant = TradingAssistant(risk_percent=risk.max_risk_percent)

    tickers = scanner.scan()
    database.save_markets(tickers)
    analysis_results = {}
    market_signals = []
    opportunities = []

    for ticker in tickers:
        result = engine.analyze(ticker.symbol)
        analysis_results[ticker.symbol] = result
        if result is None:
            continue
        market_signals.append(result.signal)
        confidence = ConfidenceEngine().evaluate(result.score)
        opportunities.append(Opportunity(
            symbol=ticker.symbol,
            score=result.score,
            confidence=confidence.score,
            signal=result.signal,
        ))

    trend = MarketTrendEngine().evaluate(market_signals)
    ranking = ranking_engine.rank(opportunities)

    print(f"\nروند کلی بازار: {trend.trend} | قدرت: {trend.strength}%")
    print_watchlist(watchlist)
    print(f"\nتعداد بازارها: {len(tickers)}")
    print(f"موجودی ثبت‌شده: {portfolio.cash:,.2f}")
    print(f"حداکثر ریسک هر معامله: {risk.max_risk_percent:.2f}%")

    print("\n" + "=" * 70)
    print("TOP OPPORTUNITIES")
    print("=" * 70)
    for index, item in enumerate(ranking, start=1):
        print(f"{index}. {item.symbol:<12} {item.signal:<8} score={item.score} confidence={item.confidence}%")

    print("\n" + "=" * 70)
    print("MARKET OVERVIEW")
    print("=" * 70)
    for ticker in tickers:
        print_ticker(ticker)

    print("\n" + "=" * 70)
    print("AI TRADING ASSISTANT")
    print("=" * 70)
    for ticker in tickers:
        print(f"\n### {ticker.symbol}")
        analyze_symbol(ticker, analysis_results.get(ticker.symbol), journal, assistant)

    print("\n" + "=" * 70)
    print("حالت ایمنی")
    print("=" * 70)
    print("✓ هیچ سفارش واقعی ارسال نمی‌شود.")
    print("✓ تصمیم نهایی با کاربر است.")
    print("✓ خروجی سیستم فقط تحلیل، هشدار و برنامه معاملاتی است.")
    print(f"✓ رکوردهای تحلیل: {journal.total_trades}")


def main() -> None:
    banner()
    run()


if __name__ == "__main__":
    main()
