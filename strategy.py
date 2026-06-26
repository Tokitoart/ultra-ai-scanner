import pandas as pd

from config import (
    EMA_FAST,
    EMA_SLOW,
    ADX_PERIOD,
    MIN_ADX,
    MIN_VOLUME_RATIO,
    MIN_ATR_PERCENT,
    RSI_PERIOD
)


# ==========================================
# EMA
# ==========================================

def ema(series, length):

    return (
        series
        .ewm(
            span=length,
            adjust=False
        )
        .mean()
    )


# ==========================================
# RSI
# ==========================================

def calculate_rsi(
    df,
    period=RSI_PERIOD
):

    delta = df["close"].diff()

    gain = delta.clip(
        lower=0
    )

    loss = (
        -delta.clip(
            upper=0
        )
    )


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


    rs = (
        avg_gain /
        avg_loss
    )


    rsi = (
        100 -
        (
            100 /
            (1 + rs)
        )
    )


    return float(
        rsi.iloc[-1]
    )



# ==========================================
# TREND
# ==========================================

def get_trend(df):

    ema50 = ema(
        df["close"],
        EMA_FAST
    ).iloc[-1]


    ema200 = ema(
        df["close"],
        EMA_SLOW
    ).iloc[-1]


    if ema50 > ema200:

        return "LONG"


    if ema50 < ema200:

        return "SHORT"


    return None



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


    plus_dm[plus_dm < 0] = 0

    minus_dm[minus_dm < 0] = 0



    tr1 = high - low

    tr2 = (
        high -
        close.shift()
    ).abs()

    tr3 = (
        low -
        close.shift()
    ).abs()


    tr = pd.concat(
        [
            tr1,
            tr2,
            tr3
        ],
        axis=1
    ).max(axis=1)


    atr = (
        tr
        .rolling(period)
        .mean()
    )


    plus_di = (
        100 *
        plus_dm
        .rolling(period)
        .mean()
        /
        atr
    )


    minus_di = (
        100 *
        minus_dm
        .rolling(period)
        .mean()
        /
        atr
    )


    dx = (

        abs(
            plus_di -
            minus_di
        )
        /
        (
            plus_di +
            minus_di
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
# ATR
# ==========================================

def calculate_atr(df, period=14):

    high = df["high"]
    low = df["low"]
    close = df["close"]


    tr1 = high-low

    tr2 = (
        high-close.shift()
    ).abs()

    tr3 = (
        low-close.shift()
    ).abs()


    tr = pd.concat(
        [
            tr1,
            tr2,
            tr3
        ],
        axis=1
    ).max(axis=1)


    return float(
        tr
        .rolling(period)
        .mean()
        .iloc[-1]
    )



# ==========================================
# ATR %
# ==========================================

def calculate_atr_percent(df):

    atr = calculate_atr(df)

    price = (
        df["close"]
        .iloc[-1]
    )


    if price <= 0:

        return 0


    return round(
        atr /
        price *
        100,
        2
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
        current /
        average,
        2
    )



# ==========================================
# ENTRY FILTER
# ==========================================

def get_entry_signal(df):

    ema20 = ema(
        df["close"],
        20
    )


    ema50 = ema(
        df["close"],
        50
    )


    price = (
        df["close"]
        .iloc[-1]
    )


    rsi = calculate_rsi(df)


    last_candle = df.iloc[-1]


    candle_size = (
        abs(
            last_candle["close"]
            -
            last_candle["open"]
        )
        /
        last_candle["open"]
        *
        100
    )


    # не покупаем после огромной свечи

    if candle_size > 1.2:

        return None



    if (
        ema20.iloc[-1]
        >
        ema50.iloc[-1]

        and

        price >
        ema20.iloc[-1]

        and

        rsi > 52
    ):

        return "LONG"



    if (
        ema20.iloc[-1]
        <
        ema50.iloc[-1]

        and

        price <
        ema20.iloc[-1]

        and

        rsi < 48
    ):

        return "SHORT"



    return None



# ==========================================
# BUILD SIGNAL
# ==========================================

def build_signal(
    symbol,
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



    # дополнительное подтверждение 1H

    trend_1h = get_trend(
        df1h
    )


    if trend != trend_1h:

        return None



    adx = calculate_adx(
        df1h
    )


    if adx < MIN_ADX:

        return None



    atr_percent = calculate_atr_percent(
        df15
    )


    if atr_percent < MIN_ATR_PERCENT:

        return None



    volume = volume_ratio(
        df5
    )


    if volume < MIN_VOLUME_RATIO:

        return None



    trigger = get_entry_signal(
        df5
    )


    if trigger != trend:

        return None



    entry = float(
        df5["close"]
        .iloc[-1]
    )


    atr = calculate_atr(
        df15
    )


    if trend == "LONG":

        sl = (
            entry -
            atr * 2
        )

    else:

        sl = (
            entry +
            atr * 2
        )



    return {

        "symbol": symbol,

        "direction": trend,

        "entry": round(
            entry,
            6
        ),

        "sl": round(
            sl,
            6
        ),

        "adx": round(
            adx,
            2
        ),

        "atr_percent": atr_percent,

        "volume_ratio": volume

    }
