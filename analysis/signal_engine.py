"""
PACT-OS
Signal Engine
"""

from __future__ import annotations


def evaluate(
    ema9: float,
    ema21: float,
    rsi14: float,
    macd: float,
    signal: float,
) -> dict:
    """
    Generate final trading signal.

    Returns
    -------
    dict
    {
        "score": int,
        "signal": str,
        "details": dict
    }
    """

    score = 0

    details = {}

    # =====================================
    # EMA
    # =====================================

    if ema9 > ema21:
        details["ema"] = "BUY"
        score += 1

    elif ema9 < ema21:
        details["ema"] = "SELL"
        score -= 1

    else:
        details["ema"] = "HOLD"

    # =====================================
    # RSI
    # =====================================

    if rsi14 <= 30:
        details["rsi"] = "BUY"
        score += 1

    elif rsi14 >= 70:
        details["rsi"] = "SELL"
        score -= 1

    else:
        details["rsi"] = "HOLD"

    # =====================================
    # MACD
    # =====================================

    if macd > signal:
        details["macd"] = "BUY"
        score += 1

    elif macd < signal:
        details["macd"] = "SELL"
        score -= 1

    else:
        details["macd"] = "HOLD"

    # =====================================
    # Final Decision
    # =====================================

    if score >= 2:
        final_signal = "STRONG BUY"

    elif score == 1:
        final_signal = "BUY"

    elif score == 0:
        final_signal = "HOLD"

    elif score == -1:
        final_signal = "SELL"

    else:
        final_signal = "STRONG SELL"

    return {
        "score": score,
        "signal": final_signal,
        "details": details,
    }