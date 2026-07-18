import pandas as pd
import numpy as np
import ta


# ==========================================
# EMA
# ==========================================

def add_ema(df):

    df["ema20"] = ta.trend.EMAIndicator(
        close=df["close"],
        window=20
    ).ema_indicator()

    df["ema50"] = ta.trend.EMAIndicator(
        close=df["close"],
        window=50
    ).ema_indicator()

    df["ema200"] = ta.trend.EMAIndicator(
        close=df["close"],
        window=200
    ).ema_indicator()

    return df


# ==========================================
# EMA SLOPE
# ==========================================

def add_ema_slope(df):

    df["ema20_slope"] = (
        df["ema20"] - df["ema20"].shift(5)
    )

    df["ema50_slope"] = (
        df["ema50"] - df["ema50"].shift(5)
    )

    return df


# ==========================================
# RSI
# ==========================================

def add_rsi(df):

    df["rsi"] = ta.momentum.RSIIndicator(
        close=df["close"],
        window=14
    ).rsi()

    return df


# ==========================================
# MACD
# ==========================================

def add_macd(df):

    macd = ta.trend.MACD(df["close"])

    df["macd"] = macd.macd()

    df["macd_signal"] = macd.macd_signal()

    df["macd_hist"] = macd.macd_diff()

    return df


# ==========================================
# ATR
# ==========================================

def add_atr(df):

    atr = ta.volatility.AverageTrueRange(

        high=df["high"],

        low=df["low"],

        close=df["close"],

        window=14

    )

    df["atr"] = atr.average_true_range()

    df["atr_percent"] = (

        df["atr"]

        /

        df["close"]

        * 100

    )

    return df


# ==========================================
# ADX
# ==========================================

def add_adx(df):

    adx = ta.trend.ADXIndicator(

        high=df["high"],

        low=df["low"],

        close=df["close"],

        window=14

    )

    df["adx"] = adx.adx()

    return df


# ==========================================
# BOLLINGER
# ==========================================

def add_bollinger(df):

    bb = ta.volatility.BollingerBands(

        close=df["close"],

        window=20,

        window_dev=2

    )

    df["bb_upper"] = bb.bollinger_hband()

    df["bb_lower"] = bb.bollinger_lband()

    df["bb_width"] = (

        (

            df["bb_upper"]

            -

            df["bb_lower"]

        )

        /

        df["close"]

        * 100

    )

    return df


# ==========================================
# VWAP
# ==========================================

def add_vwap(df):

    tp = (

        df["high"]

        +

        df["low"]

        +

        df["close"]

    ) / 3

    vwap = (

        tp * df["volume"]

    ).cumsum() / df["volume"].cumsum()

    df["vwap"] = vwap

    df["vwap_distance"] = (

        (

            df["close"]

            -

            df["vwap"]

        )

        /

        df["close"]

        * 100

    )

    return df


# ==========================================
# VOLUME RATIO
# ==========================================

def add_volume_ratio(df):

    df["volume_ma"] = (

        df["volume"]

        .rolling(20)

        .mean()

    )

    df["volume_ratio"] = (

        df["volume"]

        /

        df["volume_ma"]

    )

    return df


# ==========================================
# EMA DISTANCE
# ==========================================

def add_distances(df):

    df["ema200_distance"] = (

        (

            df["close"]

            -

            df["ema200"]

        )

        /

        df["close"]

        * 100

    )

    return df


# ==========================================
# MARKET REGIME
# ==========================================

def detect_market_regime(df):

    last = df.iloc[-1]

    if last["adx"] < 20:

        return "RANGE"

    if (

        last["ema20"]

        >

        last["ema50"]

        >

        last["ema200"]

    ):

        return "BULL"

    if (

        last["ema20"]

        <

        last["ema50"]

        <

        last["ema200"]

    ):

        return "BEAR"

    return "MIXED"


# ==========================================
# CALCULATE ALL
# ==========================================

def calculate_indicators(df):

    df = add_ema(df)

    df = add_ema_slope(df)

    df = add_rsi(df)

    df = add_macd(df)

    df = add_atr(df)

    df = add_adx(df)

    df = add_bollinger(df)

    df = add_vwap(df)

    df = add_volume_ratio(df)

    df = add_distances(df)

    return df
