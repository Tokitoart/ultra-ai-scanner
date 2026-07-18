from datetime import datetime


# ==========================================
# BUILD FEATURES
# ==========================================

def build_features(signal):

    now = datetime.utcnow()

    features = {

        # ==================================
        # TRADE
        # ==================================

        "symbol": signal.get("symbol"),

        "direction": signal.get("direction"),

        "entry": signal.get("entry"),

        # ==================================
        # TIME
        # ==================================

        "hour": now.hour,

        "weekday": now.weekday(),

        "month": now.month,

        # ==================================
        # TREND
        # ==================================

        "score": signal.get("score", 0),

        "adx": signal.get("adx", 0),

        "market_regime": signal.get(
            "market_regime",
            ""
        ),

        # ==================================
        # EMA
        # ==================================

        "ema20": signal.get("ema20", 0),

        "ema50": signal.get("ema50", 0),

        "ema200": signal.get("ema200", 0),

        "ema20_slope": signal.get(
            "ema20_slope",
            0
        ),

        "ema50_slope": signal.get(
            "ema50_slope",
            0
        ),

        "ema_distance": signal.get(
            "ema200_distance",
            0
        ),

        # ==================================
        # RSI
        # ==================================

        "rsi": signal.get("rsi", 0),

        # ==================================
        # MACD
        # ==================================

        "macd": signal.get("macd", 0),

        "macd_signal": signal.get(
            "macd_signal",
            0
        ),

        "macd_hist": signal.get(
            "macd_hist",
            0
        ),

        # ==================================
        # ATR
        # ==================================

        "atr": signal.get("atr", 0),

        "atr_percent": signal.get(
            "atr_percent",
            0
        ),

        # ==================================
        # BOLLINGER
        # ==================================

        "bb_width": signal.get(
            "bb_width",
            0
        ),

        # ==================================
        # VWAP
        # ==================================

        "vwap_distance": signal.get(
            "vwap_distance",
            0
        ),

        # ==================================
        # VOLUME
        # ==================================

        "volume_ratio": signal.get(
            "volume_ratio",
            0
        ),

        # ==================================
        # BTC FILTER
        # ==================================

        "btc_trend": signal.get(
            "btc_trend",
            0
        ),

        # ==================================
        # FUTURE AI
        # ==================================

        "spread": signal.get(
            "spread",
            0
        ),

        "funding": signal.get(
            "funding",
            0
        ),

        "oi_change": signal.get(
            "oi_change",
            0
        ),

        "liquidation_long": signal.get(
            "liq_long",
            0
        ),

        "liquidation_short": signal.get(
            "liq_short",
            0
        ),

        "news_score": signal.get(
            "news_score",
            0
        ),

        # ==================================
        # LABEL
        # ==================================

        "result": None

    }

    return features
