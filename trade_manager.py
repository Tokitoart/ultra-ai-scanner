import time
import os
import json
import psycopg2

from config import (
    START_BALANCE,
    MAX_ACTIVE_TRADES,
    BREAKEVEN_TRIGGER,
    MAX_TRADE_HOURS,
    TRAILING_START,
    TRAILING_GIVEBACK
)

from journal import save_trade


DATABASE_URL = os.getenv("DATABASE_URL")


# ==========================================
# DATABASE
# ==========================================

def get_conn():

    return psycopg2.connect(
        DATABASE_URL
    )


# ==========================================
# INIT TABLE
# ==========================================

def init_active_table():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS active_trades (

            symbol TEXT PRIMARY KEY,

            data JSONB

        )
    """)

    conn.commit()

    cur.close()
    conn.close()


# ==========================================
# ACTIVE TRADES
# ==========================================

active_trades = {}


# ==========================================
# LOAD ACTIVE TRADES
# ==========================================

def load_active_trades():

    global active_trades

    init_active_table()

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT symbol, data
        FROM active_trades
        """
    )

    rows = cur.fetchall()


    active_trades = {}

    for row in rows:

        active_trades[row[0]] = row[1]


    cur.close()
    conn.close()


    print(
        f"✅ LOADED {len(active_trades)} ACTIVE TRADES"
    )


# ==========================================
# SAVE ACTIVE TRADES
# ==========================================

def save_active_trades():

    conn = get_conn()
    cur = conn.cursor()


    for symbol, data in active_trades.items():

        cur.execute(
            """
            INSERT INTO active_trades
            (symbol,data)

            VALUES(%s,%s)

            ON CONFLICT(symbol)

            DO UPDATE SET data=%s

            """,
            (
                symbol,
                json.dumps(data),
                json.dumps(data)
            )
        )


    conn.commit()

    cur.close()
    conn.close()



# ==========================================
# DELETE ACTIVE
# ==========================================

def delete_active_trade(symbol):

    conn = get_conn()
    cur = conn.cursor()


    cur.execute(
        """
        DELETE FROM active_trades
        WHERE symbol=%s
        """,
        (symbol,)
    )


    conn.commit()

    cur.close()
    conn.close()



# ==========================================
# INIT
# ==========================================

load_active_trades()



# ==========================================
# STATS
# ==========================================

stats = {

    "balance": START_BALANCE,
    "wins": 0,
    "losses": 0,
    "total_trades": 0

}



# ==========================================
# CAN OPEN
# ==========================================

def can_open_trade():

    return (
        len(active_trades)
        <
        MAX_ACTIVE_TRADES
    )



# ==========================================
# OPEN TRADE
# ==========================================

def open_trade(signal):

    symbol = signal["symbol"]


    if symbol in active_trades:

        print(
            f"SKIP DUPLICATE TRADE {symbol}"
        )

        return


    signal["open_time"] = time.time()

    signal["highest_pnl"] = 0


    active_trades[symbol] = signal


    save_active_trades()


    print(
        f"✅ OPEN TRADE {symbol}"
    )



# ==========================================
# CLOSE TRADE
# ==========================================

def close_trade(
        symbol,
        exit_price,
        pnl,
        reason
):


    if symbol not in active_trades:

        return None


    trade = active_trades[symbol]


    save_trade(
        trade,
        exit_price,
        pnl,
        reason
    )


    stats["total_trades"] += 1


    if pnl >= 0:

        stats["wins"] += 1

    else:

        stats["losses"] += 1



    stats["balance"] *= (
        1 + pnl / 100
    )


    result = {

        "symbol": symbol,

        "direction": trade["direction"],

        "entry": trade["entry"],

        "exit": exit_price,

        "pnl": pnl,

        "reason": reason

    }



    del active_trades[symbol]


    delete_active_trade(symbol)


    print(
        f"🏁 CLOSE {symbol} {round(pnl,2)}% {reason}"
    )


    return result




# ==========================================
# BREAKEVEN
# ==========================================

def move_to_breakeven(
        trade,
        current_pnl
):


    if current_pnl < BREAKEVEN_TRIGGER:

        return trade


    if "sl" not in trade:

        return trade



    if trade["direction"] == "LONG":


        if trade["sl"] < trade["entry"]:

            trade["sl"] = trade["entry"]



    else:


        if trade["sl"] > trade["entry"]:

            trade["sl"] = trade["entry"]



    save_active_trades()


    return trade



# ==========================================
# HIGHEST PNL
# ==========================================

def update_highest_pnl(
        trade,
        pnl
):


    if pnl > trade.get(
        "highest_pnl",
        0
    ):


        trade["highest_pnl"] = pnl

        save_active_trades()



# ==========================================
# TRAILING
# ==========================================

def should_trailing_exit(
        trade,
        pnl
):


    highest = trade.get(
        "highest_pnl",
        0
    )


    if highest < TRAILING_START:

        return False


    return (
        highest - pnl
        >= TRAILING_GIVEBACK
    )



# ==========================================
# TIME EXIT
# ==========================================

def trade_expired(trade):


    elapsed = (
        time.time()
        -
        trade["open_time"]
    )


    return (
        elapsed / 3600
        >= MAX_TRADE_HOURS
    )



# ==========================================
# GET ACTIVE
# ==========================================

def get_active_trades():

    return active_trades
