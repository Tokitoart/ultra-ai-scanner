import requests
from datetime import datetime

from config import (
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID
)

# ==========================================
# SEND MESSAGE
# ==========================================

def send_message(text):

    if not TELEGRAM_TOKEN:
        print("TELEGRAM_TOKEN not found")
        return

    if not TELEGRAM_CHAT_ID:
        print("TELEGRAM_CHAT_ID not found")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:

        requests.post(
            url,
            json=payload,
            timeout=15
        )

    except Exception as e:

        print(
            "Telegram Error:",
            e
        )

# ==========================================
# STARTUP
# ==========================================

def send_startup():

    text = f"""
🚀 <b>ULTRA TREND BOT V3</b>

✅ Бот запущен

📈 Стратегия:

4H → Тренд

1H → Сила тренда

15M → Волатильность

5M → Вход

🎯 Выход:
Trailing Profit

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

    send_message(text)

# ==========================================
# NEW SIGNAL
# ==========================================

def send_signal(signal):

    emoji = (
        "🟢"
        if signal["direction"] == "LONG"
        else "🔴"
    )

    text = f"""
🚨 <b>НОВАЯ СДЕЛКА</b>

💰 Монета:
{signal["symbol"]}

{emoji} Направление:
{signal["direction"]}

🎯 Entry:
{signal["entry"]}

📈 ADX:
{signal["adx"]}

⚡ ATR:
{signal["atr_percent"]}%

📊 Volume:
x{signal["volume_ratio"]}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

    send_message(text)

# ==========================================
# CLOSE TRADE
# ==========================================

def send_close_trade(trade):

    pnl_icon = (
        "🟢"
        if trade["pnl"] >= 0
        else "🔴"
    )

    text = f"""
🏁 <b>СДЕЛКА ЗАКРЫТА</b>

💰 Монета:
{trade["symbol"]}

📈 Направление:
{trade["direction"]}

{pnl_icon} PnL:
{round(trade["pnl"], 2)}%

📌 Причина:
{trade["reason"]}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

    send_message(text)

# ==========================================
# DAILY REPORT
# ==========================================

def send_daily_report(stats):

    text = f"""
📊 <b>СТАТИСТИКА</b>

💰 Баланс:
{stats["balance"]}

🏆 Побед:
{stats["wins"]}

❌ Убыточных:
{stats["losses"]}

📈 Winrate:
{stats["winrate"]}%

📊 Сделок:
{stats["total_trades"]}
"""

    send_message(text)
