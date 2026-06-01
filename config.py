import os

# ==========================================
# TELEGRAM
# ==========================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ==========================================
# BYBIT (ПОКА НЕ ИСПОЛЬЗУЕТСЯ)
# ==========================================

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")

# ==========================================
# SCANNER
# ==========================================

SCAN_INTERVAL = 180

TOP_SYMBOLS_LIMIT = 100

MAX_ACTIVE_TRADES = 2

COOLDOWN_HOURS = 6

# ==========================================
# AI SCORE
# ==========================================

MIN_AI_SCORE = 90

BOS_SCORE = 25
CHOCH_SCORE = 25
SWEEP_SCORE = 20
VOLUME_SCORE = 15
PATTERN_SCORE = 10
TREND_SCORE = 10

# ==========================================
# RISK MANAGEMENT
# ==========================================

START_BALANCE = 1000.0

RISK_PER_TRADE = 0.01

MAX_TRADE_HOURS = 4

BREAKEVEN_TRIGGER = 0.5

PARTIAL_TP_TRIGGER = 1.0

# ==========================================
# VOLUME FILTER
# ==========================================

MIN_VOLUME_RATIO = 1.8

# ==========================================
# FLAT FILTER
# ==========================================

MIN_ATR_PERCENT = 0.4

# ==========================================
# TIMEFRAMES
# ==========================================

TREND_TF = "60"

STRUCTURE_TF = "15"

ENTRY_TF = "5"

MANAGE_TF = "1"

# ==========================================
# JOURNAL
# ==========================================

JOURNAL_FILE = "journal.csv"

# ==========================================
# STATISTICS
# ==========================================

DAILY_REPORT_HOUR = 23
