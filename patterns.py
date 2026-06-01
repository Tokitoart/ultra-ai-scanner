import numpy as np

# ==========================================
# TRIANGLE
# ==========================================

def detect_triangle(df):

    highs = df["high"].tail(40).values
    lows = df["low"].tail(40).values

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

    if high_slope < 0 and low_slope > 0:
        return "СИММЕТРИЧНЫЙ ТРЕУГОЛЬНИК"

    return None


# ==========================================
# WEDGE
# ==========================================

def detect_wedge(df):

    highs = df["high"].tail(40).values
    lows = df["low"].tail(40).values

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

    if high_slope > 0 and low_slope > 0:

        if abs(high_slope) > abs(low_slope) * 1.5:
            return "ВОСХОДЯЩИЙ КЛИН"

    if high_slope < 0 and low_slope < 0:

        if abs(low_slope) > abs(high_slope) * 1.5:
            return "НИСХОДЯЩИЙ КЛИН"

    return None


# ==========================================
# DOUBLE TOP
# ==========================================

def detect_double_top(df):

    highs = df["high"].tail(30)

    max1 = highs.max()

    highs2 = highs[
        highs < max1 * 0.999
    ]

    if len(highs2) == 0:
        return None

    max2 = highs2.max()

    diff = abs(max1 - max2) / max1

    if diff < 0.005:
        return "ДВОЙНАЯ ВЕРШИНА"

    return None


# ==========================================
# DOUBLE BOTTOM
# ==========================================

def detect_double_bottom(df):

    lows = df["low"].tail(30)

    min1 = lows.min()

    lows2 = lows[
        lows > min1 * 1.001
    ]

    if len(lows2) == 0:
        return None

    min2 = lows2.min()

    diff = abs(min1 - min2) / min1

    if diff < 0.005:
        return "ДВОЙНОЕ ДНО"

    return None


# ==========================================
# CHANNEL
# ==========================================

def detect_channel(df):

    highs = df["high"].tail(50).values
    lows = df["low"].tail(50).values

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

    slope_diff = abs(
        abs(high_slope) - abs(low_slope)
    )

    if slope_diff > abs(high_slope) * 0.5:
        return None

    if high_slope > 0 and low_slope > 0:
        return "ВОСХОДЯЩИЙ КАНАЛ"

    if high_slope < 0 and low_slope < 0:
        return "НИСХОДЯЩИЙ КАНАЛ"

    return None


# ==========================================
# FLAG
# ==========================================

def detect_flag(df):

    recent = df.tail(20)

    move = (
        recent["close"].iloc[-1]
        - recent["close"].iloc[0]
    )

    if abs(move) < recent["close"].mean() * 0.03:
        return None

    pullback = df.tail(8)

    highs = pullback["high"].values
    lows = pullback["low"].values

    hs = np.polyfit(
        range(len(highs)),
        highs,
        1
    )[0]

    ls = np.polyfit(
        range(len(lows)),
        lows,
        1
    )[0]

    if move > 0 and hs < 0 and ls < 0:
        return "БЫЧИЙ ФЛАГ"

    if move < 0 and hs > 0 and ls > 0:
        return "МЕДВЕЖИЙ ФЛАГ"

    return None


# ==========================================
# MAIN DETECTOR
# ==========================================

def detect_pattern(df):

    checks = [

        detect_triangle(df),

        detect_wedge(df),

        detect_double_top(df),

        detect_double_bottom(df),

        detect_flag(df),

        detect_channel(df)

    ]

    for pattern in checks:

        if pattern:
            return pattern

    return None
