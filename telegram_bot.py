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
        print("❌ TELEGRAM_TOKEN not found")
        return

    if not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM_CHAT_ID not found")
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

        print("Telegram Error:", e)

# ==========================================
# START MESSAGE
# ==========================================

def send_startup():

    text = f"""
🚀 <b>ULTRA AI SCANNER V2</b>

✅ Сканер запущен

📊 Режим:
Smart Money Concept

📈 TF:
1H → Тренд

15M → Структура

5M → Вход

1M → Сопровождение

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

    send_message(text)

# ==========================================
# NEW SIGNAL
# ==========================================

def send_signal(signal):

    emoji = "🟢" if signal["direction"] == "LONG" else "🔴"

    reasons_text = ""

    for reason in signal["reasons"]:
        reasons_text += f"✅ {reason}\n"

    text = f"""
🚨 <b>ULTRA ELITE ENTRY</b>

💰 <b>Монета:</b>
{signal['symbol']}

{emoji} <b>Направление:</b>
{signal['direction']}

🧠 <b>AI Score:</b>
{signal['score']}

📊 <b>Причины входа:</b>

{reasons_text}

🎯 <b>Entry:</b>
{signal['entry']}

🛑 <b>Stop Loss:</b>
{signal['sl']}

🚀 <b>Take Profit:</b>
Динамический

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

    send_message(text)

# ==========================================
# CLOSE TRADE
# ==========================================

def send_close_trade(trade):

    pnl_color = "🟢" if trade["pnl"] >= 0 else "🔴"

    text = f"""
🏁 <b>СДЕЛКА ЗАКРЫТА</b>

💰 <b>Монета:</b>
{trade['symbol']}

📈 <b>Направление:</b>
{trade['direction']}

{pnl_color} <b>PnL:</b>
{round(trade['pnl'], 2)}%

📌 <b>Причина:</b>
{trade['reason']}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

    send_message(text)

# ==========================================
# DAILY REPORT
# ==========================================

def send_daily_report(stats):

    text = f"""
📊 <b>ИТОГ ДНЯ</b>

💰 Баланс:
{round(stats['balance'], 2)}$

🏆 Побед:
{stats['wins']}

❌ Поражений:
{stats['losses']}

📈 Winrate:
{stats['winrate']}%

📊 Сделок:
{stats['total_trades']}
"""

    send_message(text)

# ==========================================
# PATTERN ALERT
# ==========================================

def send_pattern_alert(symbol, pattern, timeframe):

    text = f"""
📐 <b>ОБНАРУЖЕНА ФИГУРА</b>

💰 Монета:
{symbol}

📊 Фигура:
{pattern}

⏰ TF:
{timeframe}

👀 Проверь график вручную
"""

    send_message(text)
