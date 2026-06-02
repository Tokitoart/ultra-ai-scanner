import numpy as np

from config import (
    MIN_VOLUME_RATIO,
    MIN_ATR_PERCENT
)

# ==========================================
# BOS
# Break Of Structure
# ==========================================

def detect_bos(df):

    recent_high = df["high"].iloc[-16:-1].max()
    recent_low = df["low"].iloc[-16:-1].min()

    close = df["close"].iloc[-1]

    if close > recent_high:
        return "bull"

    if close < recent_low:
        return "bear"

    return None


# ==========================================
# CHOCH
# Change Of Character
# ==========================================

def detect_choch(df):

    highs = df["high"].tail(20).values
    lows = df["low"].tail(20).values

    high_slope = np.polyfit(
        range(len(highs)),
        highs,
        1
    )[0]

    low_slope = np.polyfit(
        range(len(lows)),
        lows,
        1
    )[0]

    if high_slope < 0 and low_slope < 0:

        recent_high = df["high"].iloc[-10:-1].max()

        if df["close"].iloc[-1] > recent_high:
            return "bull"

    if high_slope > 0 and low_slope > 0:

        recent_low = df["low"].iloc[-10:-1].min()

        if df["close"].iloc[-1] < recent_low:
            return "bear"

    return None


# ==========================================
# LIQUIDITY SWEEP
# ==========================================

def detect_liquidity_sweep(df):

    recent_low = df["low"].iloc[-21:-2].min()

    candle_low = df["low"].iloc[-2]

    candle_close = df["close"].iloc[-2]

    if candle_low < recent_low and candle_close > recent_low:
        return "bull"

    recent_high = df["high"].iloc[-21:-2].max()

    candle_high = df["high"].iloc[-2]

    if candle_high > recent_high and candle_close < recent_high:
        return "bear"

    return None


# ==========================================
# VOLUME EXPANSION
# ==========================================

def volume_expansion(df):

    current_volume = df["volume"].iloc[-1]

    avg_volume = (
        df["volume"]
        .tail(20)
        .mean()
    )

    if avg_volume == 0:
        return 0

    return round(
        current_volume / avg_volume,
        2
    )


# ==========================================
# VOLUME FILTER
# ==========================================

def volume_confirmed(df):

    ratio = volume_expansion(df)

    return ratio >= MIN_VOLUME_RATIO


# ==========================================
# FLAT FILTER
# ==========================================

def is_flat(df):

    atr = (
        (df["high"] - df["low"])
        .rolling(14)
        .mean()
        .iloc[-1]
    )

    close = df["close"].iloc[-1]

    atr_percent = (
        atr / close
    ) * 100

    return atr_percent < MIN_ATR_PERCENT


# ==========================================
# TREND
# ==========================================

def detect_trend(df):

    ema50 = (
        df["close"]
        .ewm(span=50)
        .mean()
        .iloc[-1]
    )

    ema200 = (
        df["close"]
        .ewm(span=200)
        .mean()
        .iloc[-1]
    )

    if ema50 > ema200:
        return "bull"

    if ema50 < ema200:
        return "bear"

    return "flat"


# ==========================================
# AI SCORE
# ==========================================

def calculate_ai_score(
    trend,
    bos,
    choch,
    sweep,
    volume_ratio,
    pattern=False
):

    score = 0
    reasons = []

    # Trend

    if trend in ["bull", "bear"]:

        score += 10
        reasons.append(f"Trend {trend}")

    # BOS

    if bos:

        score += 25
        reasons.append("BOS")

    # CHOCH

    if choch:

        score += 25
        reasons.append("CHOCH")

    # Sweep

    if sweep:

        score += 20
        reasons.append("Liquidity Sweep")

    # Volume

    if volume_ratio >= 3:

        score += 20
        reasons.append(
            f"Volume x{volume_ratio}"
        )

    elif volume_ratio >= 2:

        score += 15
        reasons.append(
            f"Volume x{volume_ratio}"
        )

    elif volume_ratio >= 1.8:

        score += 10
        reasons.append(
            f"Volume x{volume_ratio}"
        )

    # Pattern

    if pattern:

        score += 10
        reasons.append(pattern)

    # Multi Confirmation

    confirmations = 0

    if bos:
        confirmations += 1

    if choch:
        confirmations += 1

    if sweep:
        confirmations += 1

    if volume_ratio >= 1.8:
        confirmations += 1

    if pattern:
        confirmations += 1

    if confirmations >= 3:

        score += 15
        reasons.append(
            "Multi Confirmation"
        )

    if confirmations >= 4:

        score += 10
        reasons.append(
            "Strong Confluence"
        )

    return score, reasons


# ==========================================
# ENTRY DECISION
# ==========================================

def get_direction(
    trend,
    bos,
    choch,
    sweep
):

    bull_signals = 0
    bear_signals = 0

    for signal in [bos, choch, sweep]:

        if signal == "bull":
            bull_signals += 1

        if signal == "bear":
            bear_signals += 1

    if trend == "bull" and bull_signals >= 2:
        return "LONG"

    if trend == "bear" and bear_signals >= 2:
        return "SHORT"

    return None
