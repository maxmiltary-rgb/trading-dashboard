import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime, UTC

SYMBOL = "XAUUSD"
TIMEFRAME = mt5.TIMEFRAME_M15
LOT = 0.01

trades_today = 0
current_day = datetime.now(UTC).day

if not mt5.initialize():
    print("MT5 connection failed")
    quit()
else:
    print("Connected to MT5")


def get_data():
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 300)
    return pd.DataFrame(rates)


def get_trend():
    rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_H4, 0, 150)
    df = pd.DataFrame(rates)
    df['ma'] = df['close'].rolling(100).mean()
    return "buy" if df['close'].iloc[-1] > df['ma'].iloc[-1] else "sell"


def detect_fvg(df):
    for i in range(len(df)-10, len(df)-1):
        gap = abs(df['low'][i] - df['high'][i-2])
        if gap < 1.5:
            continue

        if df['low'][i] > df['high'][i-2]:
            return ("buy", float(df['high'][i-2]), float(df['low'][i]))

        if df['high'][i] < df['low'][i-2]:
            return ("sell", float(df['high'][i]), float(df['low'][i-2]))

    return None


def is_trading_session():
    hour = datetime.now(UTC).hour
    return (7 <= hour <= 11) or (13 <= hour <= 17)


def place_trade(direction, sl, tp):
    tick = mt5.symbol_info_tick(SYMBOL)
    price = tick.ask if direction == "buy" else tick.bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT,
        "type": mt5.ORDER_TYPE_BUY if direction == "buy" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 123456,
        "comment": "SNIPER BOT",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    print("ORDER RESULT:", result)


while True:
    print("\nBot running...")

    now = datetime.now(UTC)

    if now.day != current_day:
        trades_today = 0
        current_day = now.day

    if not is_trading_session():
        print("Outside session")
        time.sleep(60)
        continue

    if trades_today >= 3:
        print("Max trades reached")
        time.sleep(60)
        continue

    df = get_data()
    trend = get_trend()
    fvg = detect_fvg(df)

    print("Trend:", trend, "| FVG:", fvg)

    if fvg:
        direction, low, high = fvg

        if direction == trend:
            last_close = df['close'].iloc[-2]

            if low < last_close < high:
                print("Entry confirmed")

                price = df['close'].iloc[-1]

                if direction == "buy":
                    sl = low - 2
                    tp = price + (price - sl) * 2
                else:
                    sl = high + 2
                    tp = price - (sl - price) * 2

                place_trade(direction, sl, tp)
                trades_today += 1

                time.sleep(300)

    time.sleep(10)
