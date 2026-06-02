import numpy as np

# ==========================================
# SETTINGS
# ==========================================

MIN_FVG_SIZE = 0.001
MIN_OB_VOLUME_RATIO = 1.5

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

    current_price = df["close"].iloc[-1]

    # Bullish FVG

    gap_up = c3_low - c1_high

    if (
        gap_up > 0
        and gap_up > current_price * MIN_FVG_SIZE
    ):

        return {
            "type": "bull",
            "top": c3_low,
            "bottom": c1_high,
            "size": gap_up
        }

    # Bearish FVG

    gap_down = c1_low - c3_high

    if (
        gap_down > 0
        and gap_down > current_price * MIN_FVG_SIZE
    ):

        return {
            "type": "bear",
            "top": c1_low,
            "bottom": c3_high,
            "size": gap_down
        }

    return None

# ==========================================
# ORDER BLOCK
# ==========================================

def detect_order_block(df):

    if len(df) < 20:
        return None

    last = df.iloc[-1]

    body = abs(
        last["close"]
        - last["open"]
    )

    candle_range = (
        last["high"]
        - last["low"]
    )

    if candle_range <= 0:
        return None

    body_ratio = (
        body / candle_range
    )

    if body_ratio < 0.65:
        return None

    avg_volume = (
        df["volume"]
        .tail(20)
        .mean()
    )

    if avg_volume <= 0:
        return None

    volume_ratio = (
        last["volume"]
        / avg_volume
    )

    if volume_ratio < MIN_OB_VOLUME_RATIO:
        return None

    if last["close"] > last["open"]:

        return {
            "type": "bull",
            "price": float(last["low"]),
            "volume_ratio": round(
                volume_ratio,
                2
            )
        }

    if last["close"] < last["open"]:

        return {
            "type": "bear",
            "price": float(last["high"]),
            "volume_ratio": round(
                volume_ratio,
                2
            )
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

    close = (
        df["close"]
        .iloc[-1]
    )

    if close >= recent_high * 0.995:
        return "bull"

    if close <= recent_low * 1.005:
        return "bear"

    return None

# ==========================================
# PREMIUM / DISCOUNT
# ==========================================

def premium_discount_zone(df):

    if len(df) < 50:
        return None

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
        swing_high
        + swing_low
    ) / 2

    if current_price < midpoint:
        return "discount"

    return "premium"

# ==========================================
# SMC SCORE
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
