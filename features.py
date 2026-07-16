# features.py

from datetime import datetime


def build_features(

    symbol,
    direction,
    entry,

    ema20,
    ema50,
    ema200,

    rsi5,
    rsi15,

    adx,
    di_plus,
    di_minus,

    atr,
    atr_percent,

    volume,
    avg_volume,
    volume_ratio,

    price_change_5m,
    price_change_15m,
    price_change_1h,

    btc_trend

):

    features = {

        "symbol": symbol,
        "direction": direction,
        "entry": entry,

        # EMA
        "ema20": ema20,
        "ema50": ema50,
        "ema200": ema200,

        "dist_ema20":
            round((entry - ema20) / ema20 * 100, 3),

        "dist_ema50":
            round((entry - ema50) / ema50 * 100, 3),

        "dist_ema200":
            round((entry - ema200) / ema200 * 100, 3),

        # RSI
        "rsi5": rsi5,
        "rsi15": rsi15,

        # Trend
        "adx": adx,
        "di_plus": di_plus,
        "di_minus": di_minus,

        # Volatility
        "atr": atr,
        "atr_percent": atr_percent,

        # Volume
        "volume": volume,
        "avg_volume": avg_volume,
        "volume_ratio": volume_ratio,

        # Price
        "change5": price_change_5m,
        "change15": price_change_15m,
        "change1h": price_change_1h,

        # Market
        "btc_trend": btc_trend,

        # Time
        "hour": datetime.utcnow().hour,
        "weekday": datetime.utcnow().weekday()

    }

    return features
