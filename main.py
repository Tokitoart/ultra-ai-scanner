import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime

# =========================================================
# TELEGRAM
# =========================================================

BOT_TOKEN = "8723271611:AAFYDVvzWn3_iWp60fwYwBDiDAYfTLgLIq0"
CHAT_ID = "315991729"

# =========================================================
# SETTINGS
# =========================================================

SCAN_INTERVAL = 300

TIMEFRAMES = ["5m", "15m", "1H"]

sent_alerts = set()

# =========================================================
# TELEGRAM SEND
# =========================================================

def send_telegram(text):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        r = requests.post(url, json=payload, timeout=10)

        print("TG STATUS:", r.status_code)

        if r.status_code != 200:
            print(r.text)

    except Exception as e:
        print("TELEGRAM ERROR:", e)

# =========================================================
# GET TOP COINS
# =========================================================

def get_top_pairs():

    try:

        url = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

        data = requests.get(url).json()["data"]

        filtered = []

        for x in data:

            symbol = x["instId"]

            if "USDT-SWAP" not in symbol:
                continue

            vol = float(x["volCcy24h"])

            filtered.append((symbol, vol))

        filtered = sorted(filtered, key=lambda x: x[1], reverse=True)

        return [x[0] for x in filtered[:100]]

    except Exception as e:
        print("TOP COINS ERROR:", e)
        return []

# =========================================================
# GET CANDLES
# =========================================================

def get_okx_data(symbol, timeframe="15m", limit=200):

    tf_map = {
        "5m": "5m",
        "15m": "15m",
        "1H": "1H"
    }

    url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}&bar={tf_map[timeframe]}&limit={limit}"

    r = requests.get(url).json()

    data = r["data"]

    df = pd.DataFrame(data)

    df = df.iloc[:, :6]

    df.columns = ["ts", "open", "high", "low", "close", "volume"]

    df = df.astype(float)

    df = df[::-1].reset_index(drop=True)

    return df

# =========================================================
# INDICATORS
# =========================================================

def indicators(df):

    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()

    delta = df["close"].diff()

    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, abs(delta), 0)

    avg_gain = pd.Series(gain).rolling(14).mean()
    avg_loss = pd.Series(loss).rolling(14).mean()

    rs = avg_gain / avg_loss

    df["rsi"] = 100 - (100 / (1 + rs))

    return df

# =========================================================
# FIGURES
# =========================================================

def detect_patterns(df):

    closes = df["close"].values[-30:]
    highs = df["high"].values[-30:]
    lows = df["low"].values[-30:]

    pattern = None
    direction = None
    strength = 0

    # ASCENDING TRIANGLE

    if highs[-1] > highs[-5] and lows[-1] > lows[-5]:

        pattern = "ВОСХОДЯЩИЙ ТРЕУГОЛЬНИК"
        direction = "LONG"
        strength = 88

    # DESCENDING TRIANGLE

    elif highs[-1] < highs[-5] and lows[-1] < lows[-5]:

        pattern = "НИСХОДЯЩИЙ ТРЕУГОЛЬНИК"
        direction = "SHORT"
        strength = 88

    # WEDGE

    spread_now = highs[-1] - lows[-1]
    spread_old = highs[-10] - lows[-10]

    if spread_now < spread_old * 0.7:

        pattern = "КЛИН"
        strength += 5

    # CHANNEL

    slope_high = highs[-1] - highs[-10]
    slope_low = lows[-1] - lows[-10]

    if slope_high > 0 and slope_low > 0:

        pattern = "ВОСХОДЯЩИЙ КАНАЛ"
        direction = "LONG"
        strength += 8

    if slope_high < 0 and slope_low < 0:

        pattern = "НИСХОДЯЩИЙ КАНАЛ"
        direction = "SHORT"
        strength += 8

    return {
        "pattern": pattern,
        "direction": direction,
        "strength": strength
    }

# =========================================================
# ANALYSIS
# =========================================================

def analyze_symbol(symbol):

    bullish = 0
    bearish = 0

    total_score = 0

    detected_patterns = []

    last_price = None

    for tf in TIMEFRAMES:

        print("TF:", tf)

        df = get_okx_data(symbol, tf)

        df = indicators(df)

        pattern_data = detect_patterns(df)

        pattern = pattern_data["pattern"]

        if pattern:

            detected_patterns.append(f"{pattern} ({tf})")

        close = df["close"].iloc[-1]

        ema20 = df["ema20"].iloc[-1]
        ema50 = df["ema50"].iloc[-1]

        rsi = df["rsi"].iloc[-1]

        last_price = close

        score = 0

        # PRICE ACTION

        if close > ema20 > ema50:
            bullish += 1
            score += 20

        if close < ema20 < ema50:
            bearish += 1
            score += 20

        # RSI

        if 45 < rsi < 65:
            score += 15

        # VOLUME IMPULSE

        vol_now = df["volume"].iloc[-1]
        vol_avg = df["volume"].rolling(20).mean().iloc[-1]

        if vol_now > vol_avg * 1.8:
            score += 25

        # BREAKOUT

        recent_high = df["high"].rolling(20).max().iloc[-2]

        if close > recent_high:
            score += 30

        # PATTERN

        score += pattern_data["strength"]

        total_score += score

    avg_score = total_score / 3

    # =====================================================
    # FIGURE ALERTS
    # =====================================================

    for p in detected_patterns:

        alert_id = f"{symbol}_{p}"

        if alert_id not in sent_alerts:

            text = f"""
📐 <b>ФОРМИРУЕТСЯ ФИГУРА</b>

💰 Монета: <b>{symbol}</b>

📊 Фигура:
<b>{p}</b>

👀 Проверь график вручную

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

            send_telegram(text)

            sent_alerts.add(alert_id)

    # =====================================================
    # ELITE SIGNALS
    # =====================================================

    if avg_score >= 90:

        signal = "LONG" if bullish > bearish else "SHORT"

        entry = last_price

        if signal == "LONG":

            sl = round(entry * 0.995, 6)
            tp = round(entry * 1.015, 6)

        else:

            sl = round(entry * 1.005, 6)
            tp = round(entry * 0.985, 6)

        rr = 3

        alert_id = f"{symbol}_{signal}_{round(entry,4)}"

        if alert_id in sent_alerts:
            return

        text = f"""
🚨 <b>ULTRA ELITE SIGNAL</b>

💰 Монета: <b>{symbol}</b>

📈 Направление:
<b>{signal}</b>

🧠 AI Score:
<b>{round(avg_score,1)}</b>

📊 Бычьих TF:
<b>{bullish}</b>

📉 Медвежьих TF:
<b>{bearish}</b>

📐 Фигуры:
<b>{', '.join(detected_patterns) if detected_patterns else 'нет'}</b>

🎯 Entry:
<code>{entry}</code>

🛑 Stop Loss:
<code>{sl}</code>

🚀 Take Profit:
<code>{tp}</code>

⚖ Risk/Reward:
<b>{rr}</b>

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

        send_telegram(text)

        print("✅ ELITE SIGNAL:", symbol)

        sent_alerts.add(alert_id)

    else:

        print("❌ NO ELITE SETUP")

# =========================================================
# MAIN LOOP
# =========================================================

while True:

    try:

        print("\n================================================")
        print("🔥 ULTRA AI SCANNER START")
        print("================================================\n")

        pairs = get_top_pairs()

        for symbol in pairs:

            print("\nSCAN:", symbol)

            analyze_symbol(symbol)

        print("\n================================================")
        print("✅ SCAN COMPLETE")
        print("================================================")

        print(f"😴 WAIT {SCAN_INTERVAL/60} MINUTES")

        time.sleep(SCAN_INTERVAL)

    except Exception as e:

        print("MAIN ERROR:", e)

        time.sleep(30)
