import csv
import os

from datetime import datetime

from config import (
    JOURNAL_FILE,
    START_BALANCE
)


# ==========================================
# CREATE JOURNAL
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

            "time",

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

            "giveback_percent",

            "duration_minutes"

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


    open_time = trade.get(
        "open_time",
        0
    )


    duration = 0


    if open_time:

        duration = round(

            (
                datetime.now().timestamp()
                -
                open_time
            )
            /
            60,

            2
        )


    highest_pnl = trade.get(
        "highest_pnl",
        0
    )


    giveback = round(

        highest_pnl
        -
        pnl,

        2
    )


    with open(
        JOURNAL_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as f:


        writer = csv.writer(f)


        writer.writerow([


            datetime.now().strftime(
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



            highest_pnl,



            giveback,



            duration

        ])




# ==========================================
# STATS
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

            wins
            /
            trades
            *
            100,

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
        "\n========== STATS =========="
    )



    for key, value in stats.items():


        print(
            key,
            ":",
            value
        )



    print(
        "===========================\n"
    )
