import requests
import pandas as pd
import numpy as np
import time
import os
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================

TELEGRAM_TOKEN = os.getenv("8723271611:AAFYDVvzWn3_iWp60fwYwBDiDAYfTLgLIq0")
TELEGRAM_CHAT_ID = os.getenv("315991729")

SCAN_INTERVAL = 300

TIMEFRAMES = {
    "5m": "5m",
    "15m": "15m",
    "1H": "1H"
}

# cooldown
signal_cooldown = {}
pattern_cooldown = {}

SIGNAL_COOLDOWN_MIN = 120
PATTERN_COOLDOWN_MIN = 240

# =========================================================
# TELEGRAM
# =========================================================

def send_telegram(text):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

# =========================================================
# GET TOP COINS
# =========================================================

def get_top_coins():

    try:

        url = "https://www.okx.com/api/v5/public/instruments?instType=SWAP"

        data = requests.get(url).json()["data"]

        coins = []

        blacklist = [
            "USDC",
            "USDT",
            "DAI",
            "FDUSD"
        ]

        for c in data:

            symbol = c["instId"]

            if "-USDT-SWAP" not in symbol:
                continue

            bad = False

            for b in blacklist:
                if symbol.startswith(b):
                    bad = True

            if bad:
                continue

            coins.append(symbol)

        return coins[:100]

    except:
        return []

# =========================================================
# GET CANDLES
# =========================================================

def get_okx_data(symbol, tf="15m", limit=200):

    url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}&bar={tf}&limit={limit}"

    r = requests.get(url).json()

    data = r["data"]

    df = pd.DataFrame(data)

    df.columns = [
        "ts",
        "open",
        "high",
        "low",
        "close",
        "vol",
        "volccy",
        "volccyquote",
        "confirm"
    ]

    df = df.astype(float)

    df = df.iloc[::-1]

    return df

# =========================================================
# SMART MONEY ANALYSIS
# =========================================================

def analyze_market(df):

    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["vol"]

    current_price = close.iloc[-1]

    # structure
    hh = high.iloc[-1] > high.iloc[-5]
    hl = low.iloc[-1] > low.iloc[-5]

    lh = high.iloc[-1] < high.iloc[-5]
    ll = low.iloc[-1] < low.iloc[-5]

    bullish_structure = hh and hl
    bearish_structure = lh and ll

    # impulse
    impulse = abs(close.iloc[-1] - close.iloc[-5])

    avg_move = abs(close.diff()).rolling(20).mean().iloc[-1]

    strong_impulse = impulse > avg_move * 2

    # volume spike
    vol_avg = volume.rolling(20).mean().iloc[-1]
    vol_now = volume.iloc[-1]

    volume_spike = vol_now > vol_avg * 1.8

    # breakout
    breakout_up = close.iloc[-1] > high.iloc[-20:-1].max()
    breakout_down = close.iloc[-1] < low.iloc[-20:-1].min()

    # liquidity sweep
    sweep_high = high.iloc[-2] > high.iloc[-10:-2].max()
    sweep_low = low.iloc[-2] < low.iloc[-10:-2].min()

    score = 0

    if bullish_structure:
        score += 20

    if bearish_structure:
        score += 20

    if strong_impulse:
        score += 20

    if volume_spike:
        score += 20

    if breakout_up or breakout_down:
        score += 20

    # direction
    direction = "NONE"

    if bullish_structure and breakout_up:
        direction = "LONG"

    if bearish_structure and breakout_down:
        direction = "SHORT"

    return {
        "score": score,
        "direction": direction,
        "volume_spike": volume_spike,
        "breakout_up": breakout_up,
        "breakout_down": breakout_down,
        "sweep_high": sweep_high,
        "sweep_low": sweep_low,
        "price": current_price
    }

# =========================================================
# PATTERN DETECTION
# =========================================================

def detect_pattern(df):

    highs = df["high"].tail(30).values
    lows = df["low"].tail(30).values

    high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
    low_slope = np.polyfit(range(len(lows)), lows, 1)[0]

    # ascending channel
    if high_slope > 0 and low_slope > 0:
        return "ВОСХОДЯЩИЙ КАНАЛ"

    # descending channel
    if high_slope < 0 and low_slope < 0:
        return "НИСХОДЯЩИЙ КАНАЛ"

    # triangle
    if abs(high_slope) < 0.05 and low_slope > 0:
        return "ВОСХОДЯЩИЙ ТРЕУГОЛЬНИК"

    if high_slope < 0 and abs(low_slope) < 0.05:
        return "НИСХОДЯЩИЙ ТРЕУГОЛЬНИК"

    # wedge
    if high_slope < 0 and low_slope < 0 and abs(high_slope) > abs(low_slope):
        return "ПАДАЮЩИЙ КЛИН"

    if high_slope > 0 and low_slope > 0 and abs(low_slope) > abs(high_slope):
        return "РАСТУЩИЙ КЛИН"

    return None

# =========================================================
# ELITE SIGNAL
# =========================================================

def generate_signal(symbol):

    bullish = 0
    bearish = 0

    total_score = 0
    patterns = []

    direction = None

    for tf in TIMEFRAMES:

        print(f"TF: {tf}")

        df = get_okx_data(symbol, tf)

        analysis = analyze_market(df)

        pattern = detect_pattern(df)

        if pattern:
            patterns.append(f"{pattern} ({tf})")

        total_score += analysis["score"]

        if analysis["direction"] == "LONG":
            bullish += 1

        if analysis["direction"] == "SHORT":
            bearish += 1

        direction = analysis["direction"]

    avg_score = total_score / 3

    # elite filter
    elite = False

    if avg_score >= 85:

        if bullish >= 3 or bearish >= 3:
            elite = True

    return {
        "elite": elite,
        "score": round(avg_score),
        "bullish": bullish,
        "bearish": bearish,
        "direction": direction,
        "patterns": patterns
    }

# =========================================================
# MAIN LOOP
# =========================================================

while True:

    try:

        print("\n================================================")
        print("🔥 ULTRA AI SCANNER START")
        print("================================================\n")

        symbols = get_top_coins()

        signals_found = 0

        for symbol in symbols:

            try:

                print(f"SCAN: {symbol}")

                result = generate_signal(symbol)

                now = time.time()

                # =================================================
                # PATTERN ALERTS
                # =================================================

                if len(result["patterns"]) > 0:

                    if symbol not in pattern_cooldown:

                        pattern_cooldown[symbol] = 0

                    if now - pattern_cooldown[symbol] > PATTERN_COOLDOWN_MIN:

                        pattern_text = "\n".join(result["patterns"][:2])

                        text = f"""
📐 <b>ФОРМИРУЕТСЯ ФИГУРА</b>

💰 <b>Монета:</b> {symbol}

📊 <b>Обнаружено:</b>

{pattern_text}

👀 Возможна подготовка сильного движения
"""

                        send_telegram(text)

                        pattern_cooldown[symbol] = now

                # =================================================
                # ELITE SIGNALS
                # =================================================

                if result["elite"]:

                    if symbol not in signal_cooldown:
                        signal_cooldown[symbol] = 0

                    if now - signal_cooldown[symbol] > SIGNAL_COOLDOWN_MIN:

                        direction_emoji = "📈"

                        if result["direction"] == "SHORT":
                            direction_emoji = "📉"

                        text = f"""
🔥 <b>ELITE AI SIGNAL</b>

💰 <b>Монета:</b> {symbol}

{direction_emoji} <b>Направление:</b> {result["direction"]}

🧠 <b>AI Score:</b> {result["score"]}/100

📊 <b>Бычьих TF:</b> {result["bullish"]}
📉 <b>Медвежьих TF:</b> {result["bearish"]}

📐 <b>Фигуры:</b>

{chr(10).join(result["patterns"][:3])}

⚡ Сильный Smart Money setup
"""

                        send_telegram(text)

                        signal_cooldown[symbol] = now

                        signals_found += 1

                        print("✅ ELITE SIGNAL")

                else:
                    print("❌ NO ELITE SETUP")

            except Exception as e:
                print(symbol, e)

        print("\n================================================")
        print("✅ SCAN COMPLETE")
        print(f"SIGNALS FOUND: {signals_found}")
        print("================================================")

        if signals_found == 0:
            print("😴 NO ELITE SIGNALS")

        print(f"😴 WAIT {SCAN_INTERVAL/60} MINUTES")

        time.sleep(SCAN_INTERVAL)

    except Exception as e:

        print("MAIN LOOP ERROR:", e)

        time.sleep(60)
