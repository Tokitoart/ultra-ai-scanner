import numpy as np

# ==========================================
# FAIR VALUE GAP (FVG)
# ==========================================

def detect_fvg(df):

    if len(df) < 5:
        return None

    c1_high = df["high"].iloc[-3]
    c1_low = df["low"].iloc[-3]

    c3_high = df["high"].iloc[-1]
    c3_low = df["low"].iloc[-1]

    # Bullish FVG

    if c3_low > c1_high:

        return {
            "type": "bull",
            "top": c3_low,
            "bottom": c1_high
        }

    # Bearish FVG

    if c3_high < c1_low:

        return {
            "type": "bear",
            "top": c1_low,
            "bottom": c3_high
        }

    return None

# ==========================================
# ORDER BLOCK
# ==========================================

def detect_order_block(df):

    if len(df) < 10:
        return None

    last = df.iloc[-1]

    body = abs(
        last["close"] - last["open"]
    )

    candle_range = (
        last["high"] - last["low"]
    )

    if candle_range == 0:
        return None

    body_ratio = body / candle_range

    if body_ratio < 0.7:
        return None

    avg_volume = (
        df["volume"]
        .tail(20)
        .mean()
    )

    if avg_volume == 0:
        return None

    volume_ratio = (
        last["volume"] / avg_volume
    )

    if volume_ratio < 2:
        return None

    if last["close"] > last["open"]:

        return {
            "type": "bull",
            "price": last["low"]
        }

    if last["close"] < last["open"]:

        return {
            "type": "bear",
            "price": last["high"]
        }

    return None

# ==========================================
# MITIGATION BLOCK
# ==========================================

def detect_mitigation(df):

    if len(df) < 20:
        return None

    recent_high = (
        df["high"]
        .tail(20)
        .max()
    )

    recent_low = (
        df["low"]
        .tail(20)
        .min()
    )

    close = df["close"].iloc[-1]

    if close > recent_high * 0.995:

        return "bull"

    if close < recent_low * 1.005:

        return "bear"

    return None

# ==========================================
# PREMIUM / DISCOUNT
# ==========================================

def premium_discount_zone(df):

    swing_high = (
        df["high"]
        .tail(50)
        .max()
    )

    swing_low = (
        df["low"]
        .tail(50)
        .min()
    )

    current_price = (
        df["close"]
        .iloc[-1]
    )

    midpoint = (
        swing_high + swing_low
    ) / 2

    if current_price < midpoint:

        return "discount"

    return "premium"

# ==========================================
# CONFLUENCE SCORE
# ==========================================

def smc_score(
    fvg,
    order_block,
    mitigation,
    zone
):

    score = 0

    reasons = []

    if fvg:

        score += 15

        reasons.append(
            "FVG"
        )

    if order_block:

        score += 20

        reasons.append(
            "Order Block"
        )

    if mitigation:

        score += 10

        reasons.append(
            "Mitigation"
        )

    if zone == "discount":

        score += 10

        reasons.append(
            "Discount Zone"
        )

    if zone == "premium":

        score += 10

        reasons.append(
            "Premium Zone"
        )

    return score, reasons
