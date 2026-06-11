import time

from config import (
    SCAN_INTERVAL,
    COOLDOWN_HOURS
)

from data_provider import (
    get_top_symbols,
    get_klines,
    get_price,
    valid_df,
    exchange_alive
)

from strategy import build_signal

from trade_manager import (
    open_trade,
    close_trade,
    get_active_trades,
    can_open_trade,
    move_to_breakeven,
    update_highest_pnl,
    should_trailing_exit,
    trade_expired
)

from telegram_bot import (
    send_signal,
    send_startup,
    send_close_trade
)

# ==========================================
# COOLDOWN
# ==========================================

cooldown_symbols = {}

# ==========================================
# BUILD SIGNAL
# ==========================================

def get_signal(symbol):

    try:

        df4h = get_klines(
            symbol,
            "240",
            300
        )

        df1h = get_klines(
            symbol,
            "60",
            300
        )

        df15 = get_klines(
            symbol,
            "15",
            300
        )

        df5 = get_klines(
            symbol,
            "5",
            300
        )

        if not valid_df(df4h):
            return None

        if not valid_df(df1h):
            return None

        if not valid_df(df15):
            return None

        if not valid_df(df5):
            return None

        signal = build_signal(
            symbol,
            df4h,
            df1h,
            df15,
            df5
        )

        if not signal:
            return None

        signal["score"] = round(
            (
                signal["adx"]
                + signal["volume_ratio"] * 10
                + signal["atr_percent"] * 5
            ),
            2
        )

        signal["reasons"] = [
            f"ADX {signal['adx']}",
            f"Volume {signal['volume_ratio']}",
            f"ATR {signal['atr_percent']}%"
        ]

        return signal

    except Exception as e:

        print(
            f"SIGNAL ERROR {symbol}:",
            e
        )

        return None

# ==========================================
# MONITOR TRADES
# ==========================================

def monitor_trades():

    active = get_active_trades()

    closed_symbols = []

    for symbol, trade in list(active.items()):

        try:

            price = get_price(symbol)

            if price is None:
                continue

            if trade["direction"] == "LONG":

                pnl = (
                    (
                        price
                        - trade["entry"]
                    )
                    /
                    trade["entry"]
                ) * 100

                if price <= trade["sl"]:

                    send_close_trade({
                        "symbol": symbol,
                        "direction": trade["direction"],
                        "pnl": pnl,
                        "reason": "STOP LOSS"
                    })

                    close_trade(
                        symbol,
                        price,
                        pnl,
                        "STOP LOSS"
                    )

                    closed_symbols.append(
                        symbol
                    )

                    continue

            else:

                pnl = (
                    (
                        trade["entry"]
                        - price
                    )
                    /
                    trade["entry"]
                ) * 100

                if price >= trade["sl"]:

                    send_close_trade({
                        "symbol": symbol,
                        "direction": trade["direction"],
                        "pnl": pnl,
                        "reason": "STOP LOSS"
                    })

                    close_trade(
                        symbol,
                        price,
                        pnl,
                        "STOP LOSS"
                    )

                    closed_symbols.append(
                        symbol
                    )

                    continue

            update_highest_pnl(
                trade,
                pnl
            )

            move_to_breakeven(
                trade,
                pnl
            )

            if should_trailing_exit(
                trade,
                pnl
            ):

                send_close_trade({
                    "symbol": symbol,
                    "direction": trade["direction"],
                    "pnl": pnl,
                    "reason": "TRAILING EXIT"
                })

                close_trade(
                    symbol,
                    price,
                    pnl,
                    "TRAILING EXIT"
                )

                closed_symbols.append(
                    symbol
                )

                continue

            if trade_expired(trade):

                send_close_trade({
                    "symbol": symbol,
                    "direction": trade["direction"],
                    "pnl": pnl,
                    "reason": "TIME EXIT"
                })

                close_trade(
                    symbol,
                    price,
                    pnl,
                    "TIME EXIT"
                )

                closed_symbols.append(
                    symbol
                )

        except Exception as e:

            print(
                f"MONITOR ERROR {symbol}:",
                e
            )

    return closed_symbols

# ==========================================
# SCAN MARKET
# ==========================================

def scan_market():

    if not can_open_trade():
        return

    symbols = get_top_symbols()

    print(
        f"SYMBOLS FOUND: {len(symbols)}"
    )

    best_signal = None

    for symbol in symbols:

        active = get_active_trades()

        if symbol in active:
            continue
        
        if symbol in cooldown_symbols:

            elapsed = (
                time.time()
                - cooldown_symbols[symbol]
            )

            if elapsed < (
                COOLDOWN_HOURS * 3600
            ):
                continue

        signal = get_signal(symbol)

        if not signal:
            continue

        if best_signal is None:

            best_signal = signal

        elif (
            signal["score"]
            >
            best_signal["score"]
        ):

            best_signal = signal

    if not best_signal:
        return

    open_trade(
        best_signal
    )

    send_signal(
        best_signal
    )

# ==========================================
# MAIN LOOP
# ==========================================

def main():

    print(
        "===================================="
    )

    print(
        "ULTRA SCANNER STARTED"
    )

    print(
        "===================================="
    )

    if not exchange_alive():

        print(
            "WARNING: BINANCE OFFLINE"
        )

    send_startup()

    while True:

        try:

            closed = monitor_trades()

            for symbol in closed:

                cooldown_symbols[
                    symbol
                ] = time.time()

            scan_market()

            active_count = len(
                get_active_trades()
            )

            print(
                f"ACTIVE TRADES: {active_count}"
            )

            time.sleep(
                SCAN_INTERVAL
            )

        except Exception as e:

            print(
                "MAIN LOOP ERROR:",
                e
            )

            time.sleep(30)

# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":

    main()
