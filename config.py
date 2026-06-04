import os

# ==========================================
# TELEGRAM
# ==========================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ==========================================
# BYBIT
# ==========================================

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")

# ==========================================
# ACCOUNT
# ==========================================

START_BALANCE = 1000

RISK_PER_TRADE = 1.0

MAX_ACTIVE_TRADES = 2

# ==========================================
# SCANNER
# ==========================================

SCAN_INTERVAL = 180

TOP_SYMBOLS_LIMIT = 100

MIN_AI_SCORE = 50

# ==========================================
# VOLUME FILTER
# ==========================================

MIN_VOLUME_RATIO = 1.8

# ==========================================
# FLAT FILTER
# ==========================================

MIN_ATR_PERCENT = 0.4

# ==========================================
# TRADE MANAGEMENT
# ==========================================

BREAKEVEN_TRIGGER = 0.5

MAX_TRADE_HOURS = 4

# ==========================================
# JOURNAL
# ==========================================

JOURNAL_FILE = "journal.csv"

# ==========================================
# COOLDOWN
# ==========================================

COOLDOWN_HOURS = 1

# ==========================================
# AI SCORE WEIGHTS
# ==========================================

BOS_SCORE = 25

CHOCH_SCORE = 25

SWEEP_SCORE = 20

VOLUME_SCORE = 15

PATTERN_SCORE = 10

TREND_SCORE = 10

# ==========================================
# PATTERN ALERTS
# ==========================================

PATTERN_ALERT_COOLDOWN = 21600
