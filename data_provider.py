import requests
import pandas as pd
import time

from config import TOP_SYMBOLS_LIMIT

# ==========================================
# BYBIT URL
# ==========================================

BASE_URL = "https://api.bybit.com"

# ==========================================
# SAFE REQUEST
# ==========================================

def safe_request(url, params=None, retries=3):

    for _ in range(retries):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=20
            )

            if response.status_code == 200:
                return response.json()

        except Exception:
            pass

        time.sleep(1)

    return None

# ==========================================
# TOP SYMBOLS
# ==========================================

def get_top_symbols():

    try:

        url = (
            f"{BASE_URL}"
            "/v5/market/tickers"
            "?category=linear"
        )

        data = safe_request(url)

        if not data:
            return []

        tickers = data["result"]["list"]

        symbols = []

        for item in tickers:

            symbol = item["symbol"]

            if not symbol.endswith("USDT"):
                continue

            try:

                turnover = float(
                    item["turnover24h"]
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

        return [
            x[0]
            for x in symbols[
                :TOP_SYMBOLS_LIMIT
            ]
        ]

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

        url = (
            f"{BASE_URL}"
            "/v5/market/kline"
        )

        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        data = safe_request(
            url,
            params
        )

        if not data:
            return None

        rows = data["result"]["list"]

        if not rows:
            return None

        rows.reverse()

        df = pd.DataFrame(
            rows,
            columns=[
                "time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "turnover"
            ]
        )

        for col in [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "turnover"
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
            "/v5/market/tickers"
        )

        params = {
            "category": "linear",
            "symbol": symbol
        }

        data = safe_request(
            url,
            params
        )

        if not data:
            return None

        ticker_list = data["result"]["list"]

        if not ticker_list:
            return None

        return float(
            ticker_list[0]["lastPrice"]
        )

    except:

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
            "/v5/market/time"
        )

        response = requests.get(
            url,
            timeout=10
        )

        return (
            response.status_code == 200
        )

    except:

        return False

# ==========================================
# VALID DF
# ==========================================

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
