import os
import psycopg2
import json


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_conn():

    url = os.getenv("DATABASE_URL")

    if not url:
        raise Exception("DATABASE_URL NOT FOUND")

    return psycopg2.connect(url)


# ==========================================
# INIT TABLES
# ==========================================

def init_database():

    conn = get_conn()
    cur = conn.cursor()

    # Открытые сделки

    cur.execute("""
        CREATE TABLE IF NOT EXISTS active_trades (

            symbol TEXT PRIMARY KEY,

            data JSONB NOT NULL

        )
    """)

    # История сделок

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trade_history (

            id SERIAL PRIMARY KEY,

            close_time TIMESTAMP DEFAULT NOW(),

            symbol TEXT,

            direction TEXT,

            entry DOUBLE PRECISION,

            exit DOUBLE PRECISION,

            pnl DOUBLE PRECISION,

            reason TEXT,

            adx DOUBLE PRECISION,

            atr_percent DOUBLE PRECISION,

            volume_ratio DOUBLE PRECISION,

            score DOUBLE PRECISION,

            highest_pnl DOUBLE PRECISION,

            duration_minutes DOUBLE PRECISION

        )
    """)

    conn.commit()

    cur.close()
    conn.close()

    print("✅ DATABASE READY")


# ==========================================
# LOAD ACTIVE TRADES
# ==========================================

def load_trades():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""

        SELECT symbol,data

        FROM active_trades

    """)

    rows = cur.fetchall()

    trades = {}

    for row in rows:

        trades[row[0]] = row[1]

    cur.close()
    conn.close()

    print(f"✅ LOADED {len(trades)} ACTIVE TRADES FROM DATABASE")

    return trades


# ==========================================
# SAVE ACTIVE TRADES
# ==========================================

def save_trades(trades):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""

        DELETE FROM active_trades

    """)

    for symbol,data in trades.items():

        cur.execute("""

            INSERT INTO active_trades

            (
                symbol,
                data
            )

            VALUES
            (
                %s,
                %s
            )

            ON CONFLICT(symbol)

            DO UPDATE

            SET data=EXCLUDED.data

        """,(

            symbol,

            json.dumps(data)

        ))

    conn.commit()

    cur.close()
    conn.close()


# ==========================================
# SAVE CLOSED TRADE
# ==========================================

def save_trade_history(

        trade,

        exit_price,

        pnl,

        reason,

        duration

):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""

        INSERT INTO trade_history(

            symbol,

            direction,

            entry,

            exit,

            pnl,

            reason,

            adx,

            atr_percent,

            volume_ratio,

            score,

            highest_pnl,

            duration_minutes

        )

        VALUES(

            %s,%s,%s,%s,%s,%s,

            %s,%s,%s,%s,%s,%s

        )

    """,(

        trade.get("symbol"),

        trade.get("direction"),

        trade.get("entry"),

        exit_price,

        pnl,

        reason,

        trade.get("adx",0),

        trade.get("atr_percent",0),

        trade.get("volume_ratio",0),

        trade.get("score",0),

        trade.get("highest_pnl",0),

        duration

    ))

    conn.commit()

    cur.close()
    conn.close()


# ==========================================
# START DATABASE
# ==========================================

if __name__ == "__main__":

    init_database()
