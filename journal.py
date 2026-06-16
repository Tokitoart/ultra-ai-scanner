import csv
import os
from datetime import datetime

from config import (
    JOURNAL_FILE,
    START_BALANCE
)


# ==========================================
# CREATE FILE
# ==========================================

def create_journal():

    if os.path.exists(JOURNAL_FILE):
        return

    with open(
        JOURNAL_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([

            "close_time",

            "symbol",
            "direction",

            "entry",
            "exit",

            "pnl",
            "reason",

            "adx",
            "atr_percent",
            "volume_ratio",
            "score",

            "highest_pnl",

            "open_time",

            "duration_minutes",

            "sl"

        ])


# ==========================================
# SAVE TRADE
# ==========================================

def save_trade(
    trade,
    exit_price,
    pnl,
    reason
):

    create_journal()


    close_time = datetime.now()


    open_timestamp = trade.get(
        "open_time",
        0
    )


    if open_timestamp:

        open_time = datetime.fromtimestamp(
            open_timestamp
        )

        duration = int(
            (
                close_time
                - open_time
            ).total_seconds()
            / 60
        )

    else:

        open_time = close_time
        duration = 0


    with open(
        JOURNAL_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)


        writer.writerow([

            close_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),


            trade.get(
                "symbol",
                ""
            ),


            trade.get(
                "direction",
                ""
            ),


            trade.get(
                "entry",
                0
            ),


            exit_price,


            round(
                pnl,
                2
            ),


            reason,


            trade.get(
                "adx",
                0
            ),


            trade.get(
                "atr_percent",
                0
            ),


            trade.get(
                "volume_ratio",
                0
            ),


            trade.get(
                "score",
                0
            ),


            trade.get(
                "highest_pnl",
                0
            ),


            open_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),


            duration,


            trade.get(
                "sl",
                0
            )

        ])



# ==========================================
# LOAD STATS
# ==========================================

def get_stats():

    create_journal()


    wins = 0
    losses = 0

    trades = 0

    total_pnl = 0


    balance = START_BALANCE


    with open(
        JOURNAL_FILE,
        "r",
        encoding="utf-8"
    ) as f:


        reader = csv.DictReader(f)


        for row in reader:


            trades += 1


            pnl = float(
                row["pnl"]
            )


            total_pnl += pnl


            balance *= (
                1 + pnl / 100
            )


            if pnl >= 0:

                wins += 1

            else:

                losses += 1



    winrate = 0


    if trades > 0:

        winrate = round(
            wins / trades * 100,
            2
        )


    return {


        "balance": round(
            balance,
            2
        ),


        "wins": wins,


        "losses": losses,


        "total_trades": trades,


        "winrate": winrate,


        "total_pnl": round(
            total_pnl,
            2
        )

    }



# ==========================================
# PRINT STATS
# ==========================================

def print_stats():

    stats = get_stats()


    print(
        "\n=========================="
    )

    print(
        "📊 TRADING STATS"
    )

    print(
        "=========================="
    )


    print(
        "Balance:",
        stats["balance"]
    )


    print(
        "Trades:",
        stats["total_trades"]
    )


    print(
        "Wins:",
        stats["wins"]
    )


    print(
        "Losses:",
        stats["losses"]
    )


    print(
        "Winrate:",
        stats["winrate"],
        "%"
    )


    print(
        "Total PnL:",
        stats["total_pnl"],
        "%"
    )


    print(
        "==========================\n"
    )
