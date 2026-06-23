import os
import psycopg2
import json


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_conn():

    url = os.getenv(
        "DATABASE_URL"
    )

    if not url:
        raise Exception(
            "DATABASE_URL NOT FOUND"
        )

    return psycopg2.connect(
        url
    )


# ==========================================
# INIT TABLE
# ==========================================

def init_database():

    conn = get_conn()

    cur = conn.cursor()


    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS active_trades (

            symbol TEXT PRIMARY KEY,

            data JSONB NOT NULL

        )
        """
    )


    conn.commit()

    cur.close()

    conn.close()


    print(
        "✅ DATABASE READY"
    )



# ==========================================
# LOAD ACTIVE TRADES
# ==========================================

def load_trades():

    conn = get_conn()

    cur = conn.cursor()


    cur.execute(
        """
        SELECT symbol, data
        FROM active_trades
        """
    )


    rows = cur.fetchall()


    trades = {}


    for row in rows:

        trades[row[0]] = row[1]


    cur.close()

    conn.close()


    print(
        f"✅ LOADED {len(trades)} ACTIVE TRADES FROM DATABASE"
    )


    return trades



# ==========================================
# SAVE ALL TRADES
# ==========================================

def save_trades(trades):

    conn = get_conn()

    cur = conn.cursor()


    cur.execute(
        """
        DELETE FROM active_trades
        """
    )


    for symbol, data in trades.items():

        cur.execute(
            """
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
            DO UPDATE SET
            data = EXCLUDED.data

            """,
            (
                symbol,
                json.dumps(data)
            )
        )


    conn.commit()


    cur.close()

    conn.close()



# ==========================================
# START DATABASE
# ==========================================

if __name__ == "__main__":

    init_database()
