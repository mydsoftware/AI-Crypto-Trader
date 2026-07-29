"""
PACT-OS
Signal Engine
"""

from __future__ import annotations

from analysis.strategy import DefaultStrategy


def evaluate(

    ema9: float,
    ema21: float,

    rsi14: float,

    macd: float,
    signal: float,

) -> dict:

    strategy = DefaultStrategy()

    result = strategy.evaluate(

        ema9=ema9,
        ema21=ema21,

        rsi14=rsi14,

        macd=macd,
        signal=signal,

    )

    if result.score >= 2:

        final_signal = "STRONG BUY"

    elif result.score == 1:

        final_signal = "BUY"

    elif result.score == 0:

        final_signal = "HOLD"

    elif result.score == -1:

        final_signal = "SELL"

    else:

        final_signal = "STRONG SELL"

    return {

        "score": result.score,

        "signal": final_signal,

        "details": {

            "ema": result.ema,
            "rsi": result.rsi,
            "macd": result.macd,

        },
    }