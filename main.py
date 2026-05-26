import requests
import pandas as pd
import numpy as np
import time
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
from telegram import Bot

# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN = "8723271611:AAFYDVvzWn3_iWp60fwYwBDiDAYfTLgLIq0"
CHAT_ID = "315991729"

SCAN_INTERVAL = 300  # 5 минут
TIMEFRAMES = ["5m", "15m", "1H"]

bot = Bot(token=BOT_TOKEN)

# ============================================================
# TELEGRAM
# ============================================================

def send_telegram(message):
    try:
        bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode="HTML"
        )
    except Exception as e:
        print("TELEGRAM ERROR:", e)

# ============================================================
# GET TOP COINS
# ============================================================

def get_top_coins():

    url = "https://www.okx.com/api/v5/public/instruments?instType=SWAP"

    data = requests.get(url).json()["data"]

    coins = []

    blacklist = [
        "USDC",
        "USD",
        "DAI",
        "FDUSD"
    ]

    for item in data:

        symbol = item["instId"]

        if "USDT-SWAP" not in symbol:
            continue

        bad = False

        for b in blacklist:
            if b in symbol:
                bad = True

        if bad:
            continue

        coins.append(symbol)

    return coins[:100]

# ============================================================
# GET MARKET DATA
# ============================================================

def get_okx_data(symbol, timeframe="5m", limit=200):

    url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}&bar={timeframe}&limit={limit}"

    response = requests.get(url)

    data = response.json()["data"]

    df = pd.DataFrame(data)

    df.columns = [
        "ts",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "volCcy",
        "volCcyQuote",
        "confirm"
    ]

    df = df.astype(float)

    df = df[::-1]

    return df

# ============================================================
# INDICATORS
# ============================================================

def add_indicators(df):

    df["ema20"] = EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()

    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()

    macd = MACD(df["close"])

    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    atr = AverageTrueRange(
        df["high"],
        df["low"],
        df["close"],
        window=14
    )

    df["atr"] = atr.average_true_range()

    return df

# ============================================================
# AI ANALYSIS
# ============================================================

def ai_market_analysis(df):

    latest = df.iloc[-1]

    bullish_score = 0
    bearish_score = 0

    # EMA
    if latest["ema20"] > latest["ema50"]:
        bullish_score += 25
    else:
        bearish_score += 25

    # RSI
    if latest["rsi"] > 55:
        bullish_score += 20

    if latest["rsi"] < 45:
        bearish_score += 20

    # MACD
    if latest["macd"] > latest["macd_signal"]:
        bullish_score += 25
    else:
        bearish_score += 25

    # VOLUME
    avg_volume = df["volume"].tail(20).mean()

    if latest["volume"] > avg_volume:
        bullish_score += 15

    # VOLATILITY
    volatility = latest["atr"] / latest["close"]

    if volatility > 0.003:
        bullish_score += 15

    signal = "NONE"

    if bullish_score >= 85:
        signal = "BULLISH"

    if bearish_score >= 85:
        signal = "BEARISH"

    return {
        "signal": signal,
        "bullish_score": bullish_score,
        "bearish_score": bearish_score,
        "volatility": volatility
    }

# ============================================================
# MULTI TF CONFIRMATION
# ============================================================

def analyze_symbol(symbol):

    bullish_tfs = 0
    bearish_tfs = 0

    total_score = 0

    final_data = None

    for tf in TIMEFRAMES:

        print(f"TF: {tf}")

        df = get_okx_data(symbol, tf)

        df = add_indicators(df)

        analysis = ai_market_analysis(df)

        total_score += analysis["bullish_score"]

        if analysis["signal"] == "BULLISH":
            bullish_tfs += 1

        if analysis["signal"] == "BEARISH":
            bearish_tfs += 1

        final_data = df

    avg_score = total_score / len(TIMEFRAMES)

    # ONLY ELITE SETUPS
    if bullish_tfs == 3 and avg_score >= 90:

        latest = final_data.iloc[-1]

        entry = latest["close"]

        stop_loss = entry - (latest["atr"] * 1.5)

        take_profit = entry + ((entry - stop_loss) * 3)

        return {
            "symbol": symbol,
            "signal": "БЫЧИЙ",
            "score": round(avg_score, 1),
            "entry": round(entry, 4),
            "sl": round(stop_loss, 4),
            "tp": round(take_profit, 4),
            "rr": 3.0,
            "bullish_tfs": bullish_tfs
        }

    return None

# ============================================================
# BEAUTIFUL TELEGRAM MESSAGE
# ============================================================

def build_message(signal):

    return f"""
🔥 <b>ULTRA AI SIGNAL</b>

💎 <b>Монета:</b> {signal['symbol']}

📈 <b>Сигнал:</b> {signal['signal']}

🧠 <b>AI Score:</b> {signal['score']}

🎯 <b>Entry:</b> {signal['entry']}

🛑 <b>Stop Loss:</b> {signal['sl']}

🚀 <b>Take Profit:</b> {signal['tp']}

⚖ <b>Risk/Reward:</b> {signal['rr']}

📊 <b>Подтверждение TF:</b> {signal['bullish_tfs']}/3

✅ <b>ELITE SETUP DETECTED</b>
"""

# ============================================================
# MAIN LOOP
# ============================================================

while True:

    try:

        print("\n================================================")
        print("🔥 ULTRA AI SCANNER START")
        print("================================================\n")

        coins = get_top_coins()

        found_signals = []

        for symbol in coins:

            try:

                print(f"SCAN: {symbol}")

                result = analyze_symbol(symbol)

                if result:

                    print("✅ ELITE SETUP FOUND")

                    found_signals.append(result)

                else:

                    print("❌ NO ELITE SETUP")

            except Exception as e:

                print(symbol, e)

        # SORT BEST SIGNALS
        found_signals = sorted(
            found_signals,
            key=lambda x: x["score"],
            reverse=True
        )

        # SEND ONLY BEST SIGNAL
        if len(found_signals) > 0:

            best_signal = found_signals[0]

            message = build_message(best_signal)

            send_telegram(message)

            print("\n🚀 SIGNAL SENT TO TELEGRAM")

        else:

            print("\n😴 NO ELITE SIGNALS")

        print("\n================================================")
        print("✅ SCAN COMPLETE")
        print(f"SIGNALS FOUND: {len(found_signals)}")
        print("================================================")

        print(f"\n😴 WAIT {SCAN_INTERVAL/60} MINUTES")

        time.sleep(SCAN_INTERVAL)

    except Exception as e:

        print("MAIN ERROR:", e)

        time.sleep(60)
