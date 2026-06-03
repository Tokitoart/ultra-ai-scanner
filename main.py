import time

from config import (
    SCAN_INTERVAL,
    MIN_AI_SCORE,
    COOLDOWN_HOURS
)

from data_provider import (
    get_top_symbols,
    get_klines,
    get_price,
    calculate_atr,
    valid_df,
    exchange_alive
)

from market_structure import (
    detect_bos,
    detect_choch,
    detect_liquidity_sweep,
    volume_expansion,
    detect_trend,
    calculate_ai_score,
    get_direction,
    is_flat
)

from smc import (
    detect_fvg,
    detect_order_block,
    detect_mitigation,
    premium_discount_zone,
    smc_score
)

from patterns import (
    detect_pattern
)

from trade_manager import (
    open_trade,
    close_trade,
    get_active_trades,
    can_open_trade,
    move_to_breakeven,
    update_highest_pnl,
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

def build_signal(symbol):

    try:

        df1h = get_klines(
            symbol,
            "60",
            250
        )

        df15 = get_klines(
            symbol,
            "15",
            250
        )

        df5 = get_klines(
            symbol,
            "5",
            250
        )

        if not valid_df(df1h):
            return None

        if not valid_df(df15):
            return None

        if not valid_df(df5):
            return None

        if is_flat(df15):
            return None

        trend = detect_trend(
            df1h
        )

        bos = detect_bos(
            df15
        )

        choch = detect_choch(
            df15
        )

        sweep = detect_liquidity_sweep(
            df15
        )

        volume_ratio = (
            volume_expansion(df15)
        )

        pattern = detect_pattern(
            df15
        )

        direction = get_direction(
            trend,
            bos,
            choch,
            sweep
        )

        if not direction:
            return None

        score, reasons = (
            calculate_ai_score(
                trend,
                bos,
                choch,
                sweep,
                volume_ratio,
                pattern
            )
        )

        fvg = detect_fvg(df15)

        order_block = (
            detect_order_block(df15)
        )

        mitigation = (
            detect_mitigation(df15)
        )

        zone = (
            premium_discount_zone(df15)
        )

        smc_points, smc_reasons = (
            smc_score(
                fvg,
                order_block,
                mitigation,
                zone
            )
        )

        score += smc_points

        reasons.extend(
            smc_reasons
        )

        if score < MIN_AI_SCORE:
            return None

        entry = (
            df15["close"]
            .iloc[-1]
        )

        atr = calculate_atr(
            df15
        )

        if direction == "LONG":

            sl = (
                entry
                - atr * 1.5
            )

        else:

            sl = (
                entry
                + atr * 1.5
            )

        return {
            "symbol": symbol,
            "direction": direction,
            "score": round(score, 2),
            "entry": round(entry, 6),
            "sl": round(sl, 6),
            "reasons": reasons
        }

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

    remove_list = []

    for symbol, trade in list(active.items()):

        try:

            price = get_price(
                symbol
            )

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

                    remove_list.append(
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

                    remove_list.append(
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

            if trade_expired(
                trade
            ):

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

                remove_list.append(
                    symbol
                )

        except Exception as e:

            print(
                f"MONITOR ERROR {symbol}:",
                e
            )

    return remove_list

# ==========================================
# SCAN MARKET
# ==========================================

def scan_market():

    if not can_open_trade():
        return

    symbols = get_top_symbols()

    print(f"SYMBOLS FOUND: {len(symbols)}")

    best_signal = None

    for symbol in symbols:

        if symbol in cooldown_symbols:

            elapsed = (
                time.time()
                - cooldown_symbols[symbol]
            )

            if elapsed < (
                COOLDOWN_HOURS * 3600
            ):
                continue

        signal = build_signal(
            symbol
        )

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
        "=================================="
    )

    print(
        "ULTRA AI SCANNER STARTED"
    )

    print(
        "=================================="
    )

    if not exchange_alive():

        print(
            "WARNING: BYBIT HEALTH CHECK FAILED"
        )

        print(
            "CONTINUING ANYWAY..."
        )

    send_startup()

    while True:

        try:

            closed = (
                monitor_trades()
            )

            for symbol in closed:

                cooldown_symbols[
                    symbol
                ] = time.time()

            scan_market()

            active_count = len(
                get_active_trades()
            )

            print(
                f"ACTIVE: {active_count}"
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
