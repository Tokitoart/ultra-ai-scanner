import requests
import pandas as pd
import time

from config import TOP_SYMBOLS_LIMIT

# ==========================================
# BINANCE URL
# ==========================================

BASE_URL = "https://fapi.binance.com"

# ==========================================
# INTERVAL MAP
# ==========================================

INTERVAL_MAP = {
    "1": "1m",
    "3": "3m",
    "5": "5m",
    "15": "15m",
    "30": "30m",
    "60": "1h",
    "240": "4h",
    "D": "1d"
}

# ==========================================
# SAFE REQUEST
# ==========================================

def safe_request(url, params=None, retries=3):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for attempt in range(retries):

        try:

            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=20
            )

            if response.status_code == 200:
                return response.json()

            print(
                f"BINANCE HTTP ERROR: {response.status_code}"
            )

        except Exception as e:

            print(
                f"REQUEST ERROR: {e}"
            )

        time.sleep(2)

    return None

# ==========================================
# TOP SYMBOLS
# ==========================================

def get_top_symbols():

    try:

        url = (
            f"{BASE_URL}"
            "/fapi/v1/ticker/24hr"
        )

        data = safe_request(url)

        if not data:
            return []

        symbols = []

        for item in data:

            symbol = item["symbol"]

            if not symbol.endswith("USDT"):
                continue

            try:

                turnover = float(
                    item["quoteVolume"]
                )

                price = float(
                    item["lastPrice"]
                )

            except:
                continue

            if price <= 0:
                continue

            symbols.append(
                (
                    symbol,
                    turnover
                )
            )

        symbols.sort(
            key=lambda x: x[1],
            reverse=True
        )

        result = [
            x[0]
            for x in symbols[
                :TOP_SYMBOLS_LIMIT
            ]
        ]

        print(
            f"SYMBOLS FOUND: {len(result)}"
        )

        return result

    except Exception as e:

        print(
            "TOP SYMBOL ERROR:",
            e
        )

        return []

# ==========================================
# KLINES
# ==========================================

def get_klines(
    symbol,
    interval,
    limit=200
):

    try:

        interval = INTERVAL_MAP.get(
            str(interval),
            "15m"
        )

        url = (
            f"{BASE_URL}"
            "/fapi/v1/klines"
        )

        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        rows = safe_request(
            url,
            params
        )

        if not rows:
            return None

        df = pd.DataFrame(
            rows,
            columns=[
                "time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_asset_volume",
                "trades",
                "tb_base",
                "tb_quote",
                "ignore"
            ]
        )

        df = df[
            [
                "time",
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]
        ]

        for col in [
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]:

            df[col] = (
                df[col]
                .astype(float)
            )

        return df

    except Exception as e:

        print(
            f"KLINE ERROR {symbol}:",
            e
        )

        return None
# ==========================================
# CURRENT PRICE
# ==========================================

def get_price(symbol):

    try:

        url = (
            f"{BASE_URL}"
            "/fapi/v1/ticker/price"
        )

        params = {
            "symbol": symbol
        }

        data = safe_request(
            url,
            params
        )

        if not data:
            return None

        return float(
            data["price"]
        )

    except Exception as e:

        print(
            f"PRICE ERROR {symbol}:",
            e
        )

        return None

# ==========================================
# ATR
# ==========================================

def calculate_atr(
    df,
    period=14
):

    if len(df) < period + 1:
        return 0

    high = df["high"]
    low = df["low"]
    close = df["close"]

    tr1 = high - low

    tr2 = (
        high - close.shift(1)
    ).abs()

    tr3 = (
        low - close.shift(1)
    ).abs()

    tr = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    atr = (
        tr.rolling(period)
        .mean()
        .iloc[-1]
    )

    return float(atr)

# ==========================================
# HEALTH CHECK
# ==========================================

def exchange_alive():

    try:

        url = (
            f"{BASE_URL}"
            "/fapi/v1/ping"
        )

        response = requests.get(
            url,
            timeout=10
        )

        print(
            f"PING STATUS: {response.status_code}"
        )

        print(
            f"PING RESPONSE: {response.text[:500]}"
        )

        if response.status_code == 200:

            print(
                "BINANCE CONNECTION OK"
            )

            return True

        print(
            f"BINANCE HTTP ERROR: {response.status_code}"
        )

        return False

    except Exception as e:

        print(
            f"BINANCE CONNECTION ERROR: {e}"
        )

        return False

def valid_df(df):

    if df is None:
        return False

    if len(df) < 100:
        return False

    required = [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    for col in required:

        if col not in df.columns:
            return False

    return True       
