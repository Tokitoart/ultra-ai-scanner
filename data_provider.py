import requests
import pandas as pd
import time

from config import TRADING_SYMBOLS


# ==========================================
# BYBIT API
# ==========================================

BASE_URL = "https://api.bybit.com"


# ==========================================
# CHECK EXCHANGE
# ==========================================

def exchange_alive():

    try:

        r = requests.get(
            BASE_URL + "/v5/market/time",
            timeout=10
        )

        return r.status_code == 200

    except Exception as e:

        print(
            "EXCHANGE ERROR:",
            e
        )

        return False



# ==========================================
# GET SYMBOLS
# ==========================================

def get_top_symbols():

    symbols = []


    for symbol in TRADING_SYMBOLS:

        symbols.append(symbol)


    return symbols



# ==========================================
# KLINES
# ==========================================

def get_klines(
    symbol,
    interval,
    limit=300
):

    try:

        url = (
            BASE_URL
            +
            "/v5/market/kline"
        )


        params = {

            "category": "linear",

            "symbol": symbol,

            "interval": interval,

            "limit": limit

        }


        r = requests.get(
            url,
            params=params,
            timeout=10
        )


        data = r.json()


        rows = (
            data
            .get("result", {})
            .get("list", [])
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
                "turnover"
            ]
        )


        df = df.iloc[::-1]


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
# PRICE
# ==========================================

def get_price(symbol):

    try:

        url = (
            BASE_URL
            +
            "/v5/market/tickers"
        )


        params = {

            "category": "linear",

            "symbol": symbol

        }


        r = requests.get(
            url,
            params=params,
            timeout=10
        )


        data = r.json()


        ticker = (
            data
            .get("result", {})
            .get("list", [])
        )


        if not ticker:

            return None


        return float(
            ticker[0]["lastPrice"]
        )



    except Exception as e:


        print(
            f"PRICE ERROR {symbol}:",
            e
        )


        return None



# ==========================================
# DATA CHECK
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
