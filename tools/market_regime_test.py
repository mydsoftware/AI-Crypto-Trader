"""
PACT-OS
Market Regime Test
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis.market_regime import MarketRegimeEngine


def main() -> None:

    engine = MarketRegimeEngine()

    bullish_prices = [
        float(index)
        for index in range(1, 221)
    ]

    bearish_prices = [
        float(221 - index)
        for index in range(1, 221)
    ]

    bull = engine.evaluate(
        bullish_prices
    )

    bear = engine.evaluate(
        bearish_prices
    )

    print("=" * 70)
    print("PACT-OS MARKET REGIME TEST")
    print("=" * 70)

    print(
        f"Bull case : {bull.regime} "
        f"({bull.confidence:.1f}%)"
    )

    print(
        f"Bear case : {bear.regime} "
        f"({bear.confidence:.1f}%)"
    )

    assert bull.regime == "BULL"
    assert bull.bullish is True

    assert bear.regime == "BEAR"
    assert bear.bearish is True

    print("Status    : PASS")


if __name__ == "__main__":
    main()
