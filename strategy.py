import pandas as pd

from config import (
    EMA_FAST,
    EMA_SLOW,
    ADX_PERIOD,
    MIN_ADX,
    RSI_PERIOD,
    RSI_LONG_LEVEL,
    RSI_SHORT_LEVEL,
    ATR_PERIOD,
    ATR_MULTIPLIER,
    MIN_VOLUME_RATIO
)

# ==========================================
# EMA TREND
# ==========================================

def get_trend(df):

    ema_fast = (
        df["close"]
        .ewm(span=EMA_FAST)
        .mean()
        .iloc[-1]
    )

    ema_slow = (
        df["close"]
        .ewm(span=EMA_SLOW)
        .mean()
        .iloc[-1]
    )

    if ema_fast > ema_slow:
        return "LONG"

    if ema_fast < ema_slow:
        return "SHORT"

    return None

# ==========================================
# RSI
# ==========================================

def calculate_rsi(
    df,
    period=RSI_PERIOD
):

    delta = df["close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = (
        gain
        .rolling(period)
        .mean()
    )

    avg_loss = (
        loss
        .rolling(period)
        .mean()
    )

    rs = avg_gain / avg_loss

    rsi = (
        100
        - (
            100
            /
            (1 + rs)
        )
    )

    return float(
        rsi.iloc[-1]
    )

# ==========================================
# ADX
# ==========================================

def calculate_adx(
    df,
    period=ADX_PERIOD
):

    high = df["high"]
    low = df["low"]
    close = df["close"]

    plus_dm = high.diff()

    minus_dm = -low.diff()

    plus_dm[
        plus_dm < 0
    ] = 0

    minus_dm[
        minus_dm < 0
    ] = 0

    tr1 = high - low

    tr2 = (
        high
        - close.shift()
    ).abs()

    tr3 = (
        low
        - close.shift()
    ).abs()

    tr = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    atr = (
        tr
        .rolling(period)
        .mean()
    )

    plus_di = (
        100
        * (
            plus_dm
            .rolling(period)
            .mean()
            / atr
        )
    )

    minus_di = (
        100
        * (
            minus_dm
            .rolling(period)
            .mean()
            / atr
        )
    )

    dx = (
        (
            plus_di
            - minus_di
        ).abs()
        /
        (
            plus_di
            + minus_di
        )
    ) * 100

    adx = (
        dx
        .rolling(period)
        .mean()
    )

    return float(
        adx.iloc[-1]
    )

# ==========================================
# VOLUME
# ==========================================

def volume_ratio(df):

    current = (
        df["volume"]
        .iloc[-1]
    )

    average = (
        df["volume"]
        .tail(20)
        .mean()
    )

    if average <= 0:
        return 0

    return round(
        current / average,
        2
    )

# ==========================================
# ATR STOP
# ==========================================

def atr_signal(
    df,
    period=ATR_PERIOD,
    multiplier=ATR_MULTIPLIER
):

    atr = (
        (
            df["high"]
            - df["low"]
        )
        .rolling(period)
        .mean()
    )

    loss = (
        atr.iloc[-1]
        * multiplier
    )

    close_now = (
        df["close"]
        .iloc[-1]
    )

    close_prev = (
        df["close"]
        .iloc[-2]
    )

    stop_now = (
        close_now
        - loss
    )

    stop_prev = (
        close_prev
        - loss
    )

    if (
        close_prev < stop_prev
        and close_now > stop_now
    ):
        return "LONG"

    if (
        close_prev > stop_prev
        and close_now < stop_now
    ):
        return "SHORT"

    return None

# ==========================================
# ENTRY CHECK
# ==========================================

def build_signal(
    df4h,
    df1h,
    df15,
    df5
):

    trend = get_trend(
        df4h
    )

    if not trend:
        return None

    adx = calculate_adx(
        df1h
    )

    if adx < MIN_ADX:
        return None

    rsi = calculate_rsi(
        df15
    )

    if (
        trend == "LONG"
        and rsi < RSI_LONG_LEVEL
    ):
        return None

    if (
        trend == "SHORT"
        and rsi > RSI_SHORT_LEVEL
    ):
        return None

    volume = volume_ratio(
        df5
    )

    if volume < MIN_VOLUME_RATIO:
        return None

    trigger = atr_signal(
        df5
    )

    if trigger != trend:
        return None

    return {
        "direction": trend,
        "adx": round(adx, 2),
        "rsi": round(rsi, 2),
        "volume": volume
  }
