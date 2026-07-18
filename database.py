import os
import json
import psycopg2


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_conn():

    url = os.getenv("DATABASE_URL")

    if not url:
        raise Exception("DATABASE_URL NOT FOUND")

    return psycopg2.connect(url)


# ==========================================
# INIT DATABASE
# ==========================================

def init_database():

    conn = get_conn()
    cur = conn.cursor()

    # --------------------------------------
    # ACTIVE TRADES
    # --------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS active_trades(

            symbol TEXT PRIMARY KEY,

            data JSONB NOT NULL

        )
    """)

    # --------------------------------------
    # TRADE HISTORY
    # --------------------------------------

    cur.execute("""

        CREATE TABLE IF NOT EXISTS trade_history(

            id SERIAL PRIMARY KEY,

            created_at TIMESTAMP DEFAULT NOW(),

            symbol TEXT,

            direction TEXT,

            entry DOUBLE PRECISION,

            exit DOUBLE PRECISION,

            pnl DOUBLE PRECISION,

            reason TEXT,

            score DOUBLE PRECISION,

            adx DOUBLE PRECISION,

            di_plus DOUBLE PRECISION,

            di_minus DOUBLE PRECISION,

            atr DOUBLE PRECISION,

            atr_percent DOUBLE PRECISION,

            volume DOUBLE PRECISION,

            avg_volume DOUBLE PRECISION,

            volume_ratio DOUBLE PRECISION,

            ema20 DOUBLE PRECISION,

            ema50 DOUBLE PRECISION,

            ema200 DOUBLE PRECISION,

            ema_distance DOUBLE PRECISION,

            ema_slope DOUBLE PRECISION,

            rsi_5m DOUBLE PRECISION,

            rsi_15m DOUBLE PRECISION,

            macd DOUBLE PRECISION,

            macd_hist DOUBLE PRECISION,

            bb_width DOUBLE PRECISION,

            vwap_distance DOUBLE PRECISION,

            btc_trend TEXT,

            market_regime TEXT,

            price_change_5m DOUBLE PRECISION,

            price_change_15m DOUBLE PRECISION,

            price_change_1h DOUBLE PRECISION,

            hour INTEGER,

            weekday INTEGER,

            month INTEGER,

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

    for symbol, data in rows:

        trades[symbol] = data

    cur.close()
    conn.close()

    print(
        f"✅ LOADED {len(trades)} ACTIVE TRADES"
    )

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

    for symbol, data in trades.items():

        cur.execute("""

            INSERT INTO active_trades(

                symbol,

                data

            )

            VALUES(

                %s,

                %s

            )

            ON CONFLICT(symbol)

            DO UPDATE

            SET data = EXCLUDED.data

        """,

        (

            symbol,

            json.dumps(data)

        ))

    conn.commit()

    cur.close()
    conn.close()

# ==========================================
# SAVE CLOSED TRADE TO HISTORY
# ==========================================

def save_trade_history(trade):

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

            score,

            adx,
            di_plus,
            di_minus,

            atr,
            atr_percent,

            volume,
            avg_volume,
            volume_ratio,

            ema20,
            ema50,
            ema200,

            ema_distance,
            ema_slope,

            rsi_5m,
            rsi_15m,

            macd,
            macd_hist,

            bb_width,

            vwap_distance,

            btc_trend,

            market_regime,

            price_change_5m,
            price_change_15m,
            price_change_1h,

            hour,
            weekday,
            month,

            highest_pnl,
            duration_minutes

        )

        VALUES(

            %s,%s,%s,%s,%s,%s,

            %s,

            %s,%s,%s,

            %s,%s,

            %s,%s,%s,

            %s,%s,%s,

            %s,%s,

            %s,%s,

            %s,%s,

            %s,

            %s,

            %s,

            %s,

            %s,%s,%s,

            %s,%s,%s,

            %s,%s

        )

    """,

    (

        trade.get("symbol"),

        trade.get("direction"),

        trade.get("entry"),

        trade.get("exit"),

        trade.get("pnl"),

        trade.get("reason"),

        trade.get("score"),

        trade.get("adx"),

        trade.get("di_plus"),

        trade.get("di_minus"),

        trade.get("atr"),

        trade.get("atr_percent"),

        trade.get("volume"),

        trade.get("avg_volume"),

        trade.get("volume_ratio"),

        trade.get("ema20"),

        trade.get("ema50"),

        trade.get("ema200"),

        trade.get("ema_distance"),

        trade.get("ema_slope"),

        trade.get("rsi_5m"),

        trade.get("rsi_15m"),

        trade.get("macd"),

        trade.get("macd_hist"),

        trade.get("bb_width"),

        trade.get("vwap_distance"),

        trade.get("btc_trend"),

        trade.get("market_regime"),

        trade.get("price_change_5m"),

        trade.get("price_change_15m"),

        trade.get("price_change_1h"),

        trade.get("hour"),

        trade.get("weekday"),

        trade.get("month"),

        trade.get("highest_pnl"),

        trade.get("duration_minutes")

    ))

    conn.commit()

    cur.close()
    conn.close()


# ==========================================
# LOAD HISTORY
# ==========================================

def load_trade_history():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""

        SELECT *

        FROM trade_history

        ORDER BY id

    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


# ==========================================
# HISTORY COUNT
# ==========================================

def trade_history_count():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""

        SELECT COUNT(*)

        FROM trade_history

    """)

    count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return count


# ==========================================
# START
# ==========================================

if __name__ == "__main__":

    init_database()

    print(
        "Trades in history:",
        trade_history_count()
    )
