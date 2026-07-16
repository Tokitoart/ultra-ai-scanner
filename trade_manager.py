import time

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

from features import save_features

from database import (
    init_database,
    load_trades,
    save_trades
)


# ==========================================
# ACTIVE TRADES
# ==========================================

active_trades = {}


# ==========================================
# INIT DATABASE
# ==========================================

init_database()

active_trades = load_trades()


# ==========================================
# REMOVE OLD RESTORED TRADES
# ==========================================

MAX_RESTORE_HOURS = 24

valid_trades = {}


for symbol, trade in active_trades.items():

    open_time = trade.get(
        "open_time",
        time.time()
    )

    age_hours = (
        time.time()
        -
        open_time
    ) / 3600


    if age_hours <= MAX_RESTORE_HOURS:

        valid_trades[symbol] = trade


    else:

        print(
            f"🗑 REMOVE OLD TRADE {symbol}"
        )


active_trades = valid_trades


save_trades(
    active_trades
)



# ==========================================
# SAVE DATABASE
# ==========================================

def save_active_trades():

    save_trades(
        active_trades
    )



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

    save_features(
    trade,
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
# STATS
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


    return (
        drawdown >= TRAILING_GIVEBACK
    )



# ==========================================
# TIME EXIT
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


    return (
        elapsed / 3600
        >=
        MAX_TRADE_HOURS
    )



# ==========================================
# GET ACTIVE TRADES
# ==========================================

def get_active_trades():

    return active_trades
