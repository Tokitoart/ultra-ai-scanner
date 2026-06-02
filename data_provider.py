import requests
import pandas as pd

from config import (
    TOP_SYMBOLS_LIMIT
)

# ==========================================
# BYBIT URL
# ==========================================

BASE_URL = "https://api.bybit.com"

# ==========================================
# GET TOP SYMBOLS
# ==========================================

def get_top_symbols():

    try:

        url = (
            f"{BASE_URL}"
            "/v5/market/tickers"
            "?category=linear"
        )

        response = requests.get(
            url,
            timeout=20
        )

        data = response.json()

        tickers = (
            data["result"]["list"]
        )

        symbols = []

        for item in tickers:

            symbol = item["symbol"]

            if not symbol.endswith("USDT"):
                continue

            try:

                turnover = float(
                    item["turnover24h"]
                )

            except:
                turnover = 0

            symbols.append(
                (
                    symbol,
                    turnover
                )
            )

        symbols = sorted(
            symbols,
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
# GET KLINES
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

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        data = response.json()

        rows = (
            data["result"]["list"]
        )

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

        numeric_cols = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "turnover"
        ]

        for col in numeric_cols:

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
# VALID DATA
# ==========================================

def valid_df(df):

    if df is None:
        return False

    if len(df) < 100:
        return False

    return True
