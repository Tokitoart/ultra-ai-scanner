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
            "time",
            "symbol",
            "direction",
            "entry",
            "exit",
            "pnl",
            "reason"
        ])

# ==========================================
# SAVE TRADE
# ==========================================

def save_trade(
    symbol,
    direction,
    entry,
    exit_price,
    pnl,
    reason
):

    create_journal()

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
            symbol,
            direction,
            entry,
            exit_price,
            round(pnl, 2),
            reason
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

    print("\n==========================")
    print("📊 TRADING STATS")
    print("==========================")

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

    print("==========================\n")
