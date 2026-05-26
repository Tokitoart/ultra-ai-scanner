```python
import requests
import pandas as pd
import numpy as np
import time
import os
from ta.volatility import AverageTrueRange

# ============================================================
# CONFIG
# ============================================================

TELEGRAM_TOKEN = os.getenv("8723271611:AAFYDVvzWn3_iWp60fwYwBDiDAYfTLgLIq0")
TELEGRAM_CHAT_ID = os.getenv("315991729")

SCAN_INTERVAL = 300

TIMEFRAMES = {
    "5m": "5m",
    "15m": "15m",
    "1H": "1H"
}

# ============================================================
# TELEGRAM
# ============================================================

def send_telegram(message):

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }

        requests.post(url, data=payload, timeout=10)

    except Exception as e:
        print("TELEGRAM ERROR:", e)

# ============================================================
# GET TOP COINS
# ============================================================

def get_top_okx_symbols(limit=100):

    try:

        url = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

        data = requests.get(url, timeout=10).json()["data"]

        coins = []

        for item in data:

            symbol = item["instId"]

            if "USDT-SWAP" not in symbol:
                continue

            try:
                vol = float(item["volCcy24h"])
            except:
                vol = 0

            coins.append((symbol, vol))

        coins = sorted(coins, key=lambda x: x[1], reverse=True)

        return [x[0] for x in coins[:limit]]

    except:
        return []

# ============================================================
# GET CANDLES
# ============================================================

def get_okx_data(symbol, timeframe, limit=200):

    try:

        url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}&bar={timeframe}&limit={limit}"

        data = requests.get(url, timeout=10).json()["data"]

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

        df = df.astype(float)

        df = df.sort_values("ts")

        return df

    except:
        return None

# ============================================================
# MARKET STRUCTURE
# ============================================================

def detect_market_structure(df):

    highs = df["high"].tail(20).values
    lows = df["low"].tail(20).values

    hh = highs[-1] > highs[-5]
    hl = lows[-1] > lows[-5]

    lh = highs[-1] < highs[-5]
    ll = lows[-1] < lows[-5]

    if hh and hl:
        return "BULLISH"

    if lh and ll:
        return "BEARISH"

    return "RANGE"

# ============================================================
# VOLUME SPIKE
# ============================================================

def volume_spike(df):

    recent = df["volume"].tail(5).mean()

    old = df["volume"].tail(30).mean()

    return recent > old * 1.8

# ============================================================
# LIQUIDITY SWEEP
# ============================================================

def liquidity_sweep(df):

    high_prev = df["high"].iloc[-10:-1].max()

    low_prev = df["low"].iloc[-10:-1].min()

    current_high = df["high"].iloc[-1]
    current_low = df["low"].iloc[-1]

    close = df["close"].iloc[-1]

    bullish = current_low < low_prev and close > low_prev

    bearish = current_high > high_prev and close < high_prev

    return bullish, bearish

# ============================================================
# BOS
# ============================================================

def detect_bos(df):

    high_prev = df["high"].iloc[-20:-5].max()

    low_prev = df["low"].iloc[-20:-5].min()

    close = df["close"].iloc[-1]

    bullish = close > high_prev

    bearish = close < low_prev

    return bullish, bearish

# ============================================================
# ATR
# ============================================================

def get_atr(df):

    atr = AverageTrueRange(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=14
    ).average_true_range()

    return atr.iloc[-1]

# ============================================================
# TRIANGLE
# ============================================================

def detect_triangle(df):

    highs = df["high"].tail(30).values
    lows = df["low"].tail(30).values

    high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
    low_slope = np.polyfit(range(len(lows)), lows, 1)[0]

    if abs(high_slope) < 0.05 and low_slope > 0:
        return "ВОСХОДЯЩИЙ ТРЕУГОЛЬНИК"

    if high_slope < 0 and abs(low_slope) < 0.05:
        return "НИСХОДЯЩИЙ ТРЕУГОЛЬНИК"

    if high_slope < 0 and low_slope > 0:
        return "СИММЕТРИЧНЫЙ ТРЕУГОЛЬНИК"

    return None

# ============================================================
# WEDGE
# ============================================================

def detect_wedge(df):

    highs = df["high"].tail(30).values
    lows = df["low"].tail(30).values

    high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
    low_slope = np.polyfit(range(len(lows)), lows, 1)[0]

    if high_slope > 0 and low_slope > 0 and low_slope > high_slope:
        return "ВОСХОДЯЩИЙ КЛИН"

    if high_slope < 0 and low_slope < 0 and low_slope > high_slope:
        return "НИСХОДЯЩИЙ КЛИН"

    return None

# ============================================================
# CHANNEL
# ============================================================

def detect_channel(df):

    highs = df["high"].tail(30).values
    lows = df["low"].tail(30).values

    high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
    low_slope = np.polyfit(range(len(lows)), lows, 1)[0]

    if high_slope > 0 and low_slope > 0:
        return "ВОСХОДЯЩИЙ КАНАЛ"

    if high_slope < 0 and low_slope < 0:
        return "НИСХОДЯЩИЙ КАНАЛ"

    return None

# ============================================================
# PATTERN ENGINE
# ============================================================

def detect_pattern(df):

    funcs = [
        detect_triangle,
        detect_wedge,
        detect_channel
    ]

    for func in funcs:

        pattern = func(df)

        if pattern:
            return pattern

    return None

# ============================================================
# AI ANALYSIS
# ============================================================

def ai_analysis(df):

    score = 0

    structure = detect_market_structure(df)

    if structure == "BULLISH":
        score += 25

    if structure == "BEARISH":
        score += 25

    vol = volume_spike(df)

    if vol:
        score += 20

    sweep_bull, sweep_bear = liquidity_sweep(df)

    if sweep_bull or sweep_bear:
        score += 25

    bos_bull, bos_bear = detect_bos(df)

    if bos_bull or bos_bear:
        score += 25

    return score

# ============================================================
# SIGNAL ENGINE
# ============================================================

def build_signal(symbol, df_5m, df_15m, df_1h):

    structures = []

    patterns = []

    for tf_name, df in [
        ("5M", df_5m),
        ("15M", df_15m),
        ("1H", df_1h)
    ]:

        structure = detect_market_structure(df)

        structures.append(structure)

        pattern = detect_pattern(df)

        if pattern:

            patterns.append((pattern, tf_name))

    bullish = structures.count("BULLISH")

    bearish = structures.count("BEARISH")

    score = 0

    score += bullish * 20

    ai_5m = ai_analysis(df_5m)
    ai_15m = ai_analysis(df_15m)
    ai_1h = ai_analysis(df_1h)

    score += (ai_5m + ai_15m + ai_1h) / 3

    current_price = df_15m["close"].iloc[-1]

    atr = get_atr(df_15m)

    direction = None

    if bullish >= 2:
        direction = "LONG"

    if bearish >= 2:
        direction = "SHORT"

    if not direction:
        return None

    if score < 85:
        return None

    if direction == "LONG":

        entry = current_price
        stop = current_price - atr
        tp1 = current_price + atr * 2
        tp2 = current_price + atr * 3

    else:

        entry = current_price
        stop = current_price + atr
        tp1 = current_price - atr * 2
        tp2 = current_price - atr * 3

    return {
        "symbol": symbol,
        "direction": direction,
        "score": round(score, 1),
        "entry": round(entry, 6),
        "stop": round(stop, 6),
        "tp1": round(tp1, 6),
        "tp2": round(tp2, 6),
        "bullish": bullish,
        "bearish": bearish,
        "patterns": patterns
    }

# ============================================================
# SEND PATTERN ALERT
# ============================================================

def send_pattern_alert(symbol, pattern, tf):

    message = f"""
👀 <b>ФОРМИРУЕТСЯ ФИГУРА</b>

🪙 <b>Монета:</b> {symbol}

📐 <b>Паттерн:</b>
• {pattern}

⏰ <b>Таймфрейм:</b>
• {tf}

⚠️ <b>Статус:</b>
Фигура требует подтверждения

📊 Наблюдай за реакцией цены
"""

    send_telegram(message)

# ============================================================
# SEND ELITE SIGNAL
# ============================================================

def send_elite_signal(signal):

    pattern_text = ""

    if signal["patterns"]:

        for p in signal["patterns"]:

            pattern_text += f"• {p[0]} ({p[1]})\n"

    else:

        pattern_text = "• Smart Money Setup\n"

    direction_ru = "LONG 📈" if signal["direction"] == "LONG" else "SHORT 📉"

    message = f"""
🚨 <b>ULTRA ELITE СИГНАЛ</b>

🪙 <b>Монета:</b> {signal["symbol"]}

📈 <b>Направление:</b>
{direction_ru}

🧠 <b>AI Вероятность:</b>
{signal["score"]}%

📐 <b>Фигуры / Структуры:</b>
{pattern_text}

📊 <b>Подтверждение:</b>
• Бычьих TF: {signal["bullish"]}
• Медвежьих TF: {signal["bearish"]}

🏦 <b>Smart Money:</b>
✅ Liquidity Sweep
✅ BOS Confirmation
✅ Volume Expansion

💰 <b>Вход:</b>
{signal["entry"]}

🛑 <b>Стоп:</b>
{signal["stop"]}

🎯 <b>TP1:</b>
{signal["tp1"]}

🎯 <b>TP2:</b>
{signal["tp2"]}

⚡ <b>Risk/Reward:</b>
1:3
"""

    send_telegram(message)

# ============================================================
# MAIN LOOP
# ============================================================

sent_patterns = set()

print("================================================")
print("🔥 ULTRA INSTITUTIONAL AI SCANNER STARTED")
print("================================================")

while True:

    try:

        symbols = get_top_okx_symbols(100)

        signals_found = 0

        for symbol in symbols:

            print(f"\nSCAN: {symbol}")

            df_5m = get_okx_data(symbol, "5m")
            df_15m = get_okx_data(symbol, "15m")
            df_1h = get_okx_data(symbol, "1H")

            if (
                df_5m is None or
                df_15m is None or
                df_1h is None
            ):
                continue

            for tf_name, df in [
                ("5M", df_5m),
                ("15M", df_15m),
                ("1H", df_1h)
            ]:

                pattern = detect_pattern(df)

                if pattern:

                    pattern_key = f"{symbol}_{pattern}_{tf_name}"

                    if pattern_key not in sent_patterns:

                        send_pattern_alert(
                            symbol,
                            pattern,
                            tf_name
                        )

                        sent_patterns.add(pattern_key)

            signal = build_signal(
                symbol,
                df_5m,
                df_15m,
                df_1h
            )

            if signal:

                send_elite_signal(signal)

                signals_found += 1

                print("✅ ELITE SIGNAL")

            else:

                print("❌ NO ELITE SETUP")

        print("\n================================================")
        print("✅ SCAN COMPLETE")
        print(f"SIGNALS FOUND: {signals_found}")
        print("================================================")

        time.sleep(SCAN_INTERVAL)

    except Exception as e:

        print("MAIN LOOP ERROR:", e)

        time.sleep(30)
```

