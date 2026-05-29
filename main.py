import os
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================

TELEGRAM_TOKEN = os.getenv("8723271611:AAFYDVvzWn3_iWp60fwYwBDiDAYfTLgLIq0")
TELEGRAM_CHAT_ID = os.getenv("315991729")

SCAN_INTERVAL = 180
MAX_ACTIVE_TRADES = 2

RISK_PER_TRADE = 0.01
MIN_AI_SCORE = 88

TOP_SYMBOLS_LIMIT = 100

active_trades = {}
cooldown_symbols = {}

# =========================================================
# TELEGRAM
# =========================================================

def send_telegram(text):

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Telegram Error:", e)

# =========================================================
# GET TOP 100 COINS
# =========================================================

def get_top_symbols():

    try:

        url = "https://api.bybit.com/v5/market/tickers?category=linear"

        data = requests.get(url).json()

        tickers = data["result"]["list"]

        filtered = []

        for t in tickers:

            symbol = t["symbol"]

            if "USDT" not in symbol:
                continue

            volume = float(t.get("turnover24h", 0))

            filtered.append((symbol, volume))

        filtered = sorted(filtered, key=lambda x: x[1], reverse=True)

        return [x[0] for x in filtered[:TOP_SYMBOLS_LIMIT]]

    except Exception as e:
        print("Top symbols error:", e)
        return []

# =========================================================
# GET KLINES
# =========================================================

def get_klines(symbol, interval, limit=200):

    url = (
        f"https://api.bybit.com/v5/market/kline?"
        f"category=linear&symbol={symbol}"
        f"&interval={interval}&limit={limit}"
    )

    data = requests.get(url).json()

    rows = data["result"]["list"]

    rows.reverse()

    df = pd.DataFrame(rows)

    df.columns = [
        "time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "turnover"
    ]

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    return df

# =========================================================
# INDICATORS
# =========================================================

def add_indicators(df):

    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()

    delta = df["close"].diff()

    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, abs(delta), 0)

    avg_gain = pd.Series(gain).rolling(14).mean()
    avg_loss = pd.Series(loss).rolling(14).mean()

    rs = avg_gain / avg_loss

    df["rsi"] = 100 - (100 / (1 + rs))

    df["atr"] = (
        df["high"] - df["low"]
    ).rolling(14).mean()

    return df

# =========================================================
# PATTERNS
# =========================================================

def detect_pattern(df):

    highs = df["high"].tail(20).values
    lows = df["low"].tail(20).values

    high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
    low_slope = np.polyfit(range(len(lows)), lows, 1)[0]

    if high_slope > 0 and low_slope > 0:
        return "ВОСХОДЯЩИЙ КАНАЛ"

    if high_slope < 0 and low_slope < 0:
        return "НИСХОДЯЩИЙ КАНАЛ"

    if high_slope < 0 and low_slope > 0:
        return "СИММЕТРИЧНЫЙ ТРЕУГОЛЬНИК"

    return None

# =========================================================
# AI SCORE
# =========================================================

def calculate_score(df5, df15, df1h):

    score = 0

    bullish = 0
    bearish = 0

    frames = [df5, df15, df1h]

    for df in frames:

        last = df.iloc[-1]

        if last["ema20"] > last["ema50"]:
            score += 15
            bullish += 1
        else:
            score -= 10
            bearish += 1

        if last["rsi"] > 55:
            score += 10

        if last["rsi"] < 45:
            score += 10

    volatility = df15["atr"].iloc[-1]

    if volatility > df15["close"].iloc[-1] * 0.003:
        score += 15

    pattern = detect_pattern(df15)

    if pattern:
        score += 20

    return score, bullish, bearish, pattern

# =========================================================
# ENTRY LOGIC
# =========================================================

def find_trade(symbol):

    try:

        df5 = add_indicators(get_klines(symbol, "5"))
        df15 = add_indicators(get_klines(symbol, "15"))
        df1h = add_indicators(get_klines(symbol, "60"))

        score, bullish, bearish, pattern = calculate_score(
            df5,
            df15,
            df1h
        )

        if score < MIN_AI_SCORE:
            return None

        direction = None

        if bullish >= 2:
            direction = "LONG"

        if bearish >= 2:
            direction = "SHORT"

        if not direction:
            return None

        last = df15.iloc[-1]

        entry = last["close"]

        atr = last["atr"]

        if direction == "LONG":

            sl = entry - atr * 1.2
            tp = entry + atr * 2.5

        else:

            sl = entry + atr * 1.2
            tp = entry - atr * 2.5

        return {
            "symbol": symbol,
            "direction": direction,
            "score": round(score, 1),
            "entry": round(entry, 6),
            "sl": round(sl, 6),
            "tp": round(tp, 6),
            "pattern": pattern,
            "bullish": bullish,
            "bearish": bearish
        }

    except Exception as e:
        print(symbol, e)
        return None

# =========================================================
# TELEGRAM MESSAGE
# =========================================================

def send_signal(trade):

    emoji = "🟢" if trade["direction"] == "LONG" else "🔴"

    text = f"""
🚨 <b>ULTRA AI SIGNAL</b>

💰 <b>Монета:</b>
{trade['symbol']}

{emoji} <b>Направление:</b>
{trade['direction']}

🧠 <b>AI Score:</b>
{trade['score']}

📊 <b>Бычьих TF:</b>
{trade['bullish']}

📉 <b>Медвежьих TF:</b>
{trade['bearish']}

📐 <b>Фигура:</b>
{trade['pattern']}

🎯 <b>Entry:</b>
{trade['entry']}

🛑 <b>Stop Loss:</b>
{trade['sl']}

🚀 <b>Take Profit:</b>
{trade['tp']}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

    send_telegram(text)

# =========================================================
# POSITION MANAGEMENT
# =========================================================

def monitor_trade(trade):

    symbol = trade["symbol"]

    try:

        df = get_klines(symbol, "1", 50)

        price = df["close"].iloc[-1]

        pnl = 0

        if trade["direction"] == "LONG":

            pnl = ((price - trade["entry"]) / trade["entry"]) * 100

            if price >= trade["tp"]:
                close_trade(trade, pnl, "TAKE PROFIT")
                return True

            if price <= trade["sl"]:
                close_trade(trade, pnl, "STOP LOSS")
                return True

            if pnl > 0.5:
                trade["sl"] = trade["entry"]

        else:

            pnl = ((trade["entry"] - price) / trade["entry"]) * 100

            if price <= trade["tp"]:
                close_trade(trade, pnl, "TAKE PROFIT")
                return True

            if price >= trade["sl"]:
                close_trade(trade, pnl, "STOP LOSS")
                return True

            if pnl > 0.5:
                trade["sl"] = trade["entry"]

        return False

    except Exception as e:
        print("Monitor error:", e)
        return False

# =========================================================
# CLOSE TRADE
# =========================================================

def close_trade(trade, pnl, reason):

    text = f"""
🏁 <b>СДЕЛКА ЗАКРЫТА</b>

💰 <b>Монета:</b>
{trade['symbol']}

📈 <b>Направление:</b>
{trade['direction']}

📊 <b>Результат:</b>
{round(pnl, 2)}%

📌 <b>Причина:</b>
{reason}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

    send_telegram(text)

    cooldown_symbols[trade["symbol"]] = time.time()

# =========================================================
# MAIN LOOP
# =========================================================

print("================================================")
print("🔥 ULTRA AI SCANNER START")
print("================================================")

while True:

    try:

        # =============================================
        # MONITOR OPEN TRADES
        # =============================================

        remove_list = []

        for symbol, trade in active_trades.items():

            closed = monitor_trade(trade)

            if closed:
                remove_list.append(symbol)

        for r in remove_list:
            del active_trades[r]

        # =============================================
        # SEARCH NEW TRADES
        # =============================================

        if len(active_trades) < MAX_ACTIVE_TRADES:

            symbols = get_top_symbols()

            best_trade = None

            for symbol in symbols:

                print(f"SCAN: {symbol}")

                if symbol in active_trades:
                    continue

                if symbol in cooldown_symbols:

                    cd = cooldown_symbols[symbol]

                    if time.time() - cd < 3600:
                        continue

                trade = find_trade(symbol)

                if not trade:
                    continue

                if best_trade is None:
                    best_trade = trade

                elif trade["score"] > best_trade["score"]:
                    best_trade = trade

            if best_trade:

                active_trades[best_trade["symbol"]] = best_trade

                send_signal(best_trade)

                print("✅ NEW TRADE:", best_trade["symbol"])

            else:

                print("❌ NO ELITE SETUPS")

        print("================================================")
        print(f"ACTIVE TRADES: {len(active_trades)}")
        print("================================================")

        time.sleep(SCAN_INTERVAL)

    except Exception as e:

        print("MAIN ERROR:", e)

        time.sleep(30)
