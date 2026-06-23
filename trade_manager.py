# trade_manager.py

import time
import json
import os

from config import (
    START_BALANCE,
    MAX_ACTIVE_TRADES,
    BREAKEVEN_TRIGGER,
    PROFIT_LOCK_TRIGGER,
    PROFIT_LOCK_VALUE,
    MAX_TRADE_HOURS,
    TRAILING_START,
    TRAILING_GIVEBACK
)

from journal import save_trade


ACTIVE_TRADES_FILE = "active_trades.json"


# ==========================================
# ACTIVE TRADES
# ==========================================

active_trades = {}



# ==========================================
# LOAD ACTIVE TRADES
# ==========================================

def load_active_trades():

    global active_trades


    if not os.path.exists(
        ACTIVE_TRADES_FILE
    ):

        active_trades = {}
        return


    try:

        with open(
            ACTIVE_TRADES_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            active_trades = json.load(f)


        print(
            f"✅ LOADED {len(active_trades)} ACTIVE TRADES"
        )


    except Exception as e:

        print(
            "LOAD ACTIVE TRADES ERROR:",
            e
        )

        active_trades = {}



# ==========================================
# SAVE ACTIVE TRADES
# ==========================================

def save_active_trades():

    try:

        with open(
            ACTIVE_TRADES_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                active_trades,
                f,
                indent=4
            )


    except Exception as e:

        print(
            "SAVE ACTIVE TRADES ERROR:",
            e
        )



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
# CAN OPEN TRADE
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
            f"SKIP DUPLICATE TRADE: {symbol}"
        )

        return



    signal.setdefault(
        "score",
        0
    )

    signal.setdefault(
        "adx",
        0
    )

    signal.setdefault(
        "atr_percent",
        0
    )

    signal.setdefault(
        "volume_ratio",
        0
    )

    signal.setdefault(
        "highest_pnl",
        0
    )

    signal.setdefault(
        "profit_locked",
        False
    )

    signal.setdefault(
        "open_time",
        time.time()
    )


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


    closed_trade = {

        "symbol": trade.get(
            "symbol"
        ),

        "direction": trade.get(
            "direction"
        ),

        "entry": trade.get(
            "entry"
        ),

        "exit": exit_price,

        "pnl": pnl,

        "reason": reason,

        "adx": trade.get(
            "adx",
            0
        ),

        "atr_percent": trade.get(
            "atr_percent",
            0
        ),

        "volume_ratio": trade.get(
            "volume_ratio",
            0
        ),

        "score": trade.get(
            "score",
            0
        ),

        "highest_pnl": trade.get(
            "highest_pnl",
            0
        )

    }



    del active_trades[symbol]


    save_active_trades()


    print(
        f"🏁 CLOSE {symbol} "
        f"{round(pnl,2)}% "
        f"{reason}"
    )


    return closed_trade



# ==========================================
# WINRATE
# ==========================================

def get_winrate():

    trades = stats["total_trades"]


    if trades == 0:

        return 0



    return round(
        stats["wins"]
        /
        trades
        *
        100,
        2
    )



# ==========================================
# GET STATS
# ==========================================

def get_stats():

    return {

        "balance": round(
            stats["balance"],
            2
        ),

        "wins": stats["wins"],

        "losses": stats["losses"],

        "total_trades":
            stats["total_trades"],

        "winrate":
            get_winrate()

    }



# ==========================================
# MOVE STOP BREAKEVEN
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
# PROFIT LOCK
# ==========================================

def lock_profit(
    trade,
    pnl
):


    if pnl < PROFIT_LOCK_TRIGGER:

        return trade



    if trade.get(
        "profit_locked",
        False
    ):

        return trade



    entry = trade["entry"]



    if trade["direction"] == "LONG":

        trade["sl"] = (
            entry
            *
            (
                1
                +
                PROFIT_LOCK_VALUE
                /
                100
            )
        )


    else:

        trade["sl"] = (
            entry
            *
            (
                1
                -
                PROFIT_LOCK_VALUE
                /
                100
            )
        )



    trade["profit_locked"] = True


    save_active_trades()


    return trade



# ==========================================
# TRACK HIGHEST PNL
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
# TRAILING EXIT
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



    drawdown = (
        highest
        -
        pnl
    )



    if drawdown >= TRAILING_GIVEBACK:

        return True



    return False



# ==========================================
# TRADE EXPIRED
# ==========================================

def trade_expired(trade):


    elapsed = (

        time.time()

        -

        trade.get(
            "open_time",
            time.time()
        )

    )


    hours = elapsed / 3600



    return (
        hours >= MAX_TRADE_HOURS
    )



# ==========================================
# GET ACTIVE TRADES
# ==========================================

def get_active_trades():

    return active_trades
