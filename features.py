from datetime import datetime


def build_features(signal):

    now = datetime.utcnow()

    features = {

        # ==========================
        # MARKET
        # ==========================

        "symbol": signal.get("symbol"),

        "direction": signal.get("direction"),

        "entry": signal.get("entry"),

        # ==========================
        # TIME
        # ==========================

        "hour": now.hour,

        "weekday": now.weekday(),

        "month": now.month,

        # ==========================
        # TREND
        # ==========================

        "adx": signal.get("adx", 0),

        "score": signal.get("score", 0),

        # ==========================
        # VOLATILITY
        # ==========================

        "atr_percent": signal.get("atr_percent", 0),

        # ==========================
        # VOLUME
        # ==========================

        "volume_ratio": signal.get("volume_ratio", 0),

        # ==========================
        # PLACEHOLDERS
        # ==========================

        "ema_distance": 0,

        "ema_slope": 0,

        "rsi_5m": 0,

        "rsi_15m": 0,

        "macd": 0,

        "macd_hist": 0,

        "bb_width": 0,

        "vwap_distance": 0,

        "btc_trend": 0,

        "market_regime": "",

    }

    return features
