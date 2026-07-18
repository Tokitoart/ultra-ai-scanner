import pandas as pd
import numpy as np

from config import (
    EMA_FAST,
    EMA_SLOW,
    ADX_PERIOD,
    MIN_ADX,
    MIN_VOLUME_RATIO,
    MIN_ATR_PERCENT,
    RSI_PERIOD
)

from features import build_features


# =====================================================
# EMA
# =====================================================

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


# =====================================================
# RSI
# =====================================================

def calculate_rsi(df, period=RSI_PERIOD):

    delta = df["close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return float(rsi.iloc[-1])


# =====================================================
# MACD
# =====================================================

def calculate_macd(df):

    ema12 = ema(df["close"], 12)
    ema26 = ema(df["close"], 26)

    macd = ema12 - ema26

    signal = macd.ewm(span=9).mean()

    hist = macd - signal

    return (
        float(macd.iloc[-1]),
        float(signal.iloc[-1]),
        float(hist.iloc[-1])
    )


# =====================================================
# ATR
# =====================================================

def calculate_atr(df, period=14):

    high = df["high"]
    low = df["low"]
    close = df["close"]

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()

    tr = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    return float(
        tr.rolling(period).mean().iloc[-1]
    )


def calculate_atr_percent(df):

    atr = calculate_atr(df)

    price = df["close"].iloc[-1]

    return round(
        atr / price * 100,
        3
    )


# =====================================================
# ADX
# =====================================================

def calculate_adx(df, period=ADX_PERIOD):

    high = df["high"]
    low = df["low"]
    close = df["close"]

    plus_dm = high.diff()
    minus_dm = -low.diff()

    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()

    tr = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    atr = tr.rolling(period).mean()

    plus_di = (
        100
        * plus_dm.rolling(period).mean()
        / atr
    )

    minus_di = (
        100
        * minus_dm.rolling(period).mean()
        / atr
    )

    dx = (
        abs(
            plus_di - minus_di
        )
        /
        (
            plus_di + minus_di
        )
    ) * 100

    adx = dx.rolling(period).mean()

    return {
        "adx": float(adx.iloc[-1]),
        "di_plus": float(plus_di.iloc[-1]),
        "di_minus": float(minus_di.iloc[-1])
    }


# =====================================================
# Bollinger Bands
# =====================================================

def bollinger_width(df):

    ma = df["close"].rolling(20).mean()

    std = df["close"].rolling(20).std()

    upper = ma + std * 2
    lower = ma - std * 2

    width = (
        upper.iloc[-1]
        -
        lower.iloc[-1]
    )

    return round(
        width / ma.iloc[-1] * 100,
        3
    )


# =====================================================
# VWAP
# =====================================================

def calculate_vwap(df):

    typical = (
        df["high"]
        +
        df["low"]
        +
        df["close"]
    ) / 3

    vwap = (
        (
            typical
            *
            df["volume"]
        ).cumsum()
        /
        df["volume"].cumsum()
    )

    return float(
        vwap.iloc[-1]
    )


# =====================================================
# VOLUME
# =====================================================

def volume_stats(df):

    current = float(
        df["volume"].iloc[-1]
    )

    average = float(
        df["volume"]
        .tail(20)
        .mean()
    )

    ratio = round(
        current / average,
        2
    )

    return {

        "volume": current,

        "avg_volume": average,

        "volume_ratio": ratio

    }

# =====================================================
# PRICE CHANGE
# =====================================================

def price_change(df, candles):

    if len(df) <= candles:
        return 0

    current = df["close"].iloc[-1]
    previous = df["close"].iloc[-candles - 1]

    return round(
        (current - previous)
        / previous
        * 100,
        3
    )


# =====================================================
# TREND
# =====================================================

def get_trend(df):

    ema_fast = ema(
        df["close"],
        EMA_FAST
    ).iloc[-1]

    ema_slow = ema(
        df["close"],
        EMA_SLOW
    ).iloc[-1]

    if ema_fast > ema_slow:
        return "LONG"

    if ema_fast < ema_slow:
        return "SHORT"

    return None


# =====================================================
# ENTRY SIGNAL
# =====================================================

def get_entry_signal(df):

    ema20 = ema(df["close"], 20)
    ema50 = ema(df["close"], 50)

    price = df["close"].iloc[-1]

    rsi = calculate_rsi(df)

    candle = df.iloc[-1]

    candle_size = abs(
        candle["close"] -
        candle["open"]
    ) / candle["open"] * 100

    if candle_size > 1.2:
        return None

    if (
        ema20.iloc[-1] > ema50.iloc[-1]
        and price > ema20.iloc[-1]
        and rsi > 52
    ):
        return "LONG"

    if (
        ema20.iloc[-1] < ema50.iloc[-1]
        and price < ema20.iloc[-1]
        and rsi < 48
    ):
        return "SHORT"

    return None


# =====================================================
# MARKET REGIME
# =====================================================

def market_regime(adx, atr_percent):

    if adx >= 40:

        if atr_percent >= 0.8:
            return "STRONG_VOLATILE"

        return "STRONG"

    if adx >= 25:

        if atr_percent >= 0.8:
            return "TREND_VOLATILE"

        return "TREND"

    if atr_percent >= 1.2:
        return "CHAOTIC"

    return "RANGE"


# =====================================================
# BUILD SIGNAL
# =====================================================

def build_signal(
    symbol,
    df4h,
    df1h,
    df15,
    df5
):

    trend = get_trend(df4h)

    if trend is None:
        return None

    trend1h = get_trend(df1h)

    if trend != trend1h:
        return None

    adx_data = calculate_adx(df1h)

    if adx_data["adx"] < MIN_ADX:
        return None

    atr = calculate_atr(df15)

    atr_percent = calculate_atr_percent(df15)

    if atr_percent < MIN_ATR_PERCENT:
        return None

    volume = volume_stats(df5)

    if volume["volume_ratio"] < MIN_VOLUME_RATIO:
        return None

    trigger = get_entry_signal(df5)

    if trigger != trend:
        return None

    entry = float(
        df5["close"].iloc[-1]
    )

    ema20 = float(
        ema(df5["close"], 20).iloc[-1]
    )

    ema50 = float(
        ema(df1h["close"], 50).iloc[-1]
    )

    ema200 = float(
        ema(df4h["close"], 200).iloc[-1]
    )

    ema_distance = round(
        (
            entry - ema20
        )
        / entry
        * 100,
        3
    )

    ema_slope = round(
        ema20 -
        float(
            ema(df5["close"],20).iloc[-2]
        ),
        6
    )

    rsi5 = round(
        calculate_rsi(df5),
        2
    )

    rsi15 = round(
        calculate_rsi(df15),
        2
    )

    macd,
    macd_signal,
    macd_hist = calculate_macd(df15)

    bb_width = bollinger_width(df15)

    vwap = calculate_vwap(df15)

    vwap_distance = round(
        (
            entry - vwap
        )
        / entry
        * 100,
        3
    )

    regime = market_regime(
        adx_data["adx"],
        atr_percent
    )
    
    change5 = price_change(df5, 1)

    change15 = price_change(df15, 1)

    change1h = price_change(df1h, 1)

    btc_trend = trend

    signal = build_features({

        "symbol": symbol,

        "direction": trend,

        "entry": entry,

        "hour": 0,

        "weekday": 0,

        "month": 0,

        "adx": round(
            adx_data["adx"],
            2
        ),

        "score": round(

            adx_data["adx"]

            +

            volume["volume_ratio"] * 10,

            2

        ),

        "atr_percent": atr_percent,

        "volume_ratio": volume["volume_ratio"],

        "ema_distance": ema_distance,

        "ema_slope": ema_slope,

        "rsi_5m": rsi5,

        "rsi_15m": rsi15,

        "macd": round(macd, 6),

        "macd_hist": round(macd_hist, 6),

        "bb_width": bb_width,

        "vwap_distance": vwap_distance,

        "btc_trend": btc_trend,

        "market_regime": regime,

        "ema20": round(ema20, 6),

        "ema50": round(ema50, 6),

        "ema200": round(ema200, 6),

        "di_plus": round(
            adx_data["di_plus"],
            2
        ),

        "di_minus": round(
            adx_data["di_minus"],
            2
        ),

        "atr": round(
            atr,
            6
        ),

        "volume": volume["volume"],

        "avg_volume": volume["avg_volume"],

        "price_change_5m": change5,

        "price_change_15m": change15,

        "price_change_1h": change1h

    })


    if trend == "LONG":

        signal["sl"] = round(
            entry - atr * 2,
            6
        )

    else:

        signal["sl"] = round(
            entry + atr * 2,
            6
        )


    return signal

