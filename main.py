import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime

# ============================================================
# TELEGRAM
# ============================================================

BOT_TOKEN = "8723271611:AAFYDVvzWn3_iWp60fwYwBDiDAYfTLgLIq0"
CHAT_ID = "315991729"

# ============================================================
# SETTINGS
# ============================================================

SCAN_INTERVAL = 300

MIN_VOLUME_24H = 5_000_000

ELITE_SCORE = 115

MAX_SIGNALS_PER_SCAN = 2
MAX_PATTERNS_PER_SCAN = 4

SIGNAL_COOLDOWN = 1800
PATTERN_COOLDOWN = 7200

TIMEFRAMES = [
    ("5m", "5m"),
    ("15m", "15m"),
    ("1H", "1H")
]

# ============================================================
# MEMORY
# ============================================================

LAST_SIGNAL_TIME = {}
LAST_PATTERN_TIME = {}

# ============================================================
# TELEGRAM
# ============================================================

def send_telegram(text):

    try:

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }

        requests.post(url, data=payload, timeout=10)

    except Exception as e:
        print("TELEGRAM ERROR:", e)

# ============================================================
# GET TOP COINS
# ============================================================

def get_top_100_okx_pairs():

    try:

        url = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

        data = requests.get(url).json()["data"]

        pairs = []

        for x in data:

            try:

                symbol = x["instId"]

                if "USDT-SWAP" not in symbol:
                    continue

                vol = float(x["volCcy24h"])

                if vol < MIN_VOLUME_24H:
                    continue

                pairs.append((symbol, vol))

            except:
                pass

        pairs = sorted(pairs, key=lambda x: x[1], reverse=True)

        return [x[0] for x in pairs[:100]]

    except Exception as e:

        print("TOP COINS ERROR:", e)

        return []

# ============================================================
# GET CANDLES
# ============================================================

def get_candles(symbol, tf="15m", limit=200):

    try:

        url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}&bar={tf}&limit={limit}"

        data = requests.get(url).json()["data"]

        df = pd.DataFrame(data)

        df = df.iloc[:, :6]

        df.columns = [
            "ts",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]

        for col in ["open","high","low","close","volume"]:
            df[col] = df[col].astype(float)

        df = df[::-1].reset_index(drop=True)

        return df

    except:
        return None

# ============================================================
# MARKET STRUCTURE
# ============================================================

def market_structure(df):

    highs = df["high"].values
    lows = df["low"].values

    bullish = 0
    bearish = 0

    if highs[-1] > highs[-5]:
        bullish += 1
    else:
        bearish += 1

    if lows[-1] > lows[-5]:
        bullish += 1
    else:
        bearish += 1

    return bullish, bearish

# ============================================================
# VOLUME PRESSURE
# ============================================================

def volume_pressure(df):

    recent = df["volume"].tail(10).mean()

    old = df["volume"].tail(50).mean()

    ratio = recent / old

    if ratio > 1.5:
        return "HIGH"

    elif ratio > 1.1:
        return "NORMAL"

    else:
        return "LOW"

# ============================================================
# LIQUIDITY SWEEP
# ============================================================

def liquidity_sweep(df):

    high_break = df["high"].iloc[-1] > df["high"].iloc[-5:-1].max()

    low_break = df["low"].iloc[-1] < df["low"].iloc[-5:-1].min()

    if high_break:
        return "BUY SIDE"

    if low_break:
        return "SELL SIDE"

    return "NONE"

# ============================================================
# VOLATILITY
# ============================================================

def volatility(df):

    return (df["high"] - df["low"]).rolling(20).mean().iloc[-1]

# ============================================================
# COMPRESSION
# ============================================================

def compression(df):

    recent = volatility(df)

    old = (df["high"] - df["low"]).rolling(50).mean().iloc[-1]

    if recent < old * 0.7:
        return "HIGH"

    return "NORMAL"

# ============================================================
# PATTERN DETECTION
# ============================================================

def detect_pattern(df):

    highs = df["high"].tail(20).values
    lows = df["low"].tail(20).values

    high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
    low_slope = np.polyfit(range(len(lows)), lows, 1)[0]

    # ASCENDING CHANNEL
    if high_slope > 0 and low_slope > 0:
        return "ВОСХОДЯЩИЙ КАНАЛ", 7

    # DESCENDING CHANNEL
    if high_slope < 0 and low_slope < 0:
        return "НИСХОДЯЩИЙ КАНАЛ", 7

    # TRIANGLE
    if high_slope < 0 and low_slope > 0:
        return "СИММЕТРИЧНЫЙ ТРЕУГОЛЬНИК", 9

    # FALLING WEDGE
    if high_slope < 0 and low_slope < 0 and abs(low_slope) < abs(high_slope):
        return "ПАДАЮЩИЙ КЛИН", 9

    # RISING WEDGE
    if high_slope > 0 and low_slope > 0 and abs(low_slope) > abs(high_slope):
        return "РАСТУЩИЙ КЛИН", 9

    return None, 0

# ============================================================
# AI ANALYSIS
# ============================================================

def analyze_symbol(symbol):

    bullish_tf = 0
    bearish_tf = 0

    patterns = []

    total_score = 0

    best_tf = None

    pattern_strength = 0

    compression_state = "NORMAL"

    liquidity = "NONE"

    volume_state = "LOW"

    entry = None

    sl = None

    tp = None

    side = None

    for tf_name, tf in TIMEFRAMES:

        print(f"TF: {tf}")

        df = get_candles(symbol, tf)

        if df is None:
            continue

        bull, bear = market_structure(df)

        bullish_tf += bull
        bearish_tf += bear

        pattern, strength = detect_pattern(df)

        if pattern:
            patterns.append(f"{pattern} ({tf})")

        volume_state = volume_pressure(df)

        liquidity = liquidity_sweep(df)

        compression_state = compression(df)

        if strength > pattern_strength:
            pattern_strength = strength
            best_tf = tf

        total_score += strength

        price = df["close"].iloc[-1]

        atr = (df["high"] - df["low"]).rolling(14).mean().iloc[-1]

        if bull > bear:

            side = "LONG"

            entry = round(price, 6)

            sl = round(price - atr * 1.5, 6)

            tp = round(price + atr * 4.5, 6)

        else:

            side = "SHORT"

            entry = round(price, 6)

            sl = round(price + atr * 1.5, 6)

            tp = round(price - atr * 4.5, 6)

    rr = 3

    score = total_score

    if bullish_tf >= 5:
        score += 20

    if bearish_tf >= 5:
        score += 20

    if volume_state == "HIGH":
        score += 15

    if compression_state == "HIGH":
        score += 15

    if liquidity != "NONE":
        score += 15

    elite = score >= ELITE_SCORE

    pattern_only = (
        pattern_strength >= 8
        and not elite
    )

    probability = min(round(score), 99)

    return {
        "elite": elite,
        "pattern_only": pattern_only,
        "score": score,
        "side": side,
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "rr": rr,
        "bullish_tf": bullish_tf,
        "bearish_tf": bearish_tf,
        "pattern": ", ".join(patterns),
        "pattern_strength": pattern_strength,
        "tf_pattern": best_tf,
        "compression": compression_state,
        "liquidity": liquidity,
        "volume_state": volume_state,
        "probability": probability
    }

# ============================================================
# MAIN LOOP
# ============================================================

while True:

    try:

        print("\n" + "="*60)
        print("🔥 ULTRA SMART AI SCANNER")
        print("="*60)

        signals_sent = 0
        patterns_sent = 0

        pairs = get_top_100_okx_pairs()

        print(f"COINS: {len(pairs)}")

        for symbol in pairs:

            try:

                print(f"\nSCAN: {symbol}")

                signal = analyze_symbol(symbol)

                now = time.time()

                # ===================================================
                # ELITE SIGNAL
                # ===================================================

                if signal["elite"]:

                    if signals_sent >= MAX_SIGNALS_PER_SCAN:
                        continue

                    last = LAST_SIGNAL_TIME.get(symbol, 0)

                    if now - last < SIGNAL_COOLDOWN:
                        continue

                    LAST_SIGNAL_TIME[symbol] = now

                    send_telegram(
f"""
🚨 <b>ULTRA ELITE SIGNAL</b>

💰 <b>Монета:</b>
{symbol}

📈 <b>Направление:</b>
{signal['side']}

🧠 <b>AI Score:</b>
{round(signal['score'],1)}

📊 <b>Бычьих TF:</b>
{signal['bullish_tf']}

📉 <b>Медвежьих TF:</b>
{signal['bearish_tf']}

📐 <b>Фигуры:</b>
{signal['pattern']}

🎯 <b>Entry:</b>
{signal['entry']}

🛑 <b>Stop Loss:</b>
{signal['sl']}

🚀 <b>Take Profit:</b>
{signal['tp']}

⚖ <b>RR:</b>
{signal['rr']}

🔥 <b>Вероятность:</b>
{signal['probability']}%

💧 <b>Liquidity Sweep:</b>
{signal['liquidity']}

📦 <b>Volume Pressure:</b>
{signal['volume_state']}

⚡ <b>Compression:</b>
{signal['compression']}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""
                    )

                    print("✅ ELITE SIGNAL SENT")

                    signals_sent += 1

                # ===================================================
                # PATTERN ALERT
                # ===================================================

                elif signal["pattern_only"]:

                    if patterns_sent >= MAX_PATTERNS_PER_SCAN:
                        continue

                    last = LAST_PATTERN_TIME.get(symbol, 0)

                    if now - last < PATTERN_COOLDOWN:
                        continue

                    LAST_PATTERN_TIME[symbol] = now

                    send_telegram(
f"""
📐 <b>ФОРМИРУЕТСЯ ФИГУРА</b>

💰 <b>Монета:</b>
{symbol}

📊 <b>Фигура:</b>
{signal['pattern']}

⏰ <b>Таймфрейм:</b>
{signal['tf_pattern']}

🔥 <b>Сила фигуры:</b>
{signal['pattern_strength']}/10

⚡ <b>Compression:</b>
{signal['compression']}

👀 Проверь график вручную

⏰ {datetime.now().strftime('%H:%M:%S')}
"""
                    )

                    print("📐 PATTERN ALERT SENT")

                    patterns_sent += 1

            except Exception as e:

                print(symbol, e)

        print("\n" + "="*60)
        print("✅ SCAN COMPLETE")
        print(f"🚨 SIGNALS SENT: {signals_sent}")
        print(f"📐 PATTERNS SENT: {patterns_sent}")
        print("="*60)

        print(f"😴 WAIT {SCAN_INTERVAL/60} MINUTES")

        time.sleep(SCAN_INTERVAL)

    except Exception as e:

        print("MAIN LOOP ERROR:", e)

        time.sleep(60)
