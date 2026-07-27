"""
PACT-OS Configuration
"""

from pathlib import Path

# Project
APP_NAME = "PACT-OS"
VERSION = "0.1.0"

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

# Database
DATABASE_PATH = DATA_DIR / "pact.db"

# Exchange
EXCHANGE_NAME = "Tabdeal"

# Watchlist
WATCHLIST = [
    "BTC_IRT",
    "ETH_IRT",
    "SOL_IRT",
    "XRP_IRT",
]

# Timeframes
DEFAULT_TIMEFRAME = "1h"

# Indicators
EMA_FAST = 20
EMA_MID = 50
EMA_SLOW = 200

RSI_PERIOD = 14

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9