import os
import psycopg2
from datetime import datetime

from config import START_BALANCE

# ==========================================
# DATABASE
# ==========================================

DATABASE_URL = os.getenv("DATABASE_URL")

# ==========================================
# CONNECT
# ==========================================

def get_conn():
    return psycopg2.connect(DATABASE_URL)

# ==========================================
# INIT TABLE
# ==========================================

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            time TIMESTAMP,
            symbol TEXT,
            direction TEXT,
            entry DOUBLE PRECISION,
            exit DOUBLE PRECISION,
            pnl DOUBLE PRECISION,
            reason TEXT,
            adx DOUBLE PRECISION,
            atr_percent DOUBLE PRECISION,
            volume_ratio DOUBLE PRECISION,
            score DOUBLE PRECISION
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

# ==========================================
# SAVE TRADE
# ==========================================

def save_trade(
    trade,
    exit_price,
    pnl,
    reason
):

    init_db()

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO trades (
            time,
            symbol,
            direction,
            entry,
            exit,
            pnl,
            reason,
            adx,
            atr_percent,
            volume_ratio,
            score
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        datetime.now(),
        trade["symbol"],
        trade["direction"],
        trade["entry"],
        exit_price,
        pnl,
        reason,
        trade.get("adx", 0),
        trade.get("atr_percent", 0),
        trade.get("volume_ratio", 0),
        trade.get("score", 0)
    ))

    conn.commit()
    cur.close()
    conn.close()

# ==========================================
# LOAD STATS
# ==========================================

def get_stats():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT pnl FROM trades")

    rows = cur.fetchall()

    wins = 0
    losses = 0
    total = 0
    balance = START_BALANCE

    for r in rows:

        pnl = float(r[0])
        total += 1
        balance *= (1 + pnl / 100)

        if pnl >= 0:
            wins += 1
        else:
            losses += 1

    winrate = 0

    if total > 0:
        winrate = round(wins / total * 100, 2)

    cur.close()
    conn.close()

    return {
        "balance": round(balance, 2),
        "wins": wins,
        "losses": losses,
        "total_trades": total,
        "winrate": winrate
    }

# ==========================================
# PRINT STATS
# ==========================================

def print_stats():

    stats = get_stats()

    print("\n==========================")
    print("📊 TRADING STATS (POSTGRES)")
    print("==========================")

    print("Balance:", stats["balance"])
    print("Trades:", stats["total_trades"])
    print("Wins:", stats["wins"])
    print("Losses:", stats["losses"])
    print("Winrate:", stats["winrate"], "%")

    print("==========================\n")
