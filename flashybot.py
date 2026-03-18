import MetaTrader5 as mt5
import pandas as pd
import time

# -------- SETTINGS --------
SYMBOL = "XAUUSD"
TIMEFRAME = mt5.TIMEFRAME_M1

BASE_LOT = 0.01
lot = BASE_LOT

SL_POINTS = 200
TP_POINTS = 300

MAX_TRADES = 5

# -------- CONNECT --------
if not mt5.initialize():
    print("MT5 failed")
    quit()

print("✅ MT5 Connected")

# -------- GET DATA --------
def get_data():
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 100)
    df = pd.DataFrame(rates)

    df['ema50'] = df['close'].ewm(span=50).mean()

    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    return df

# -------- COUNT TRADES --------
def count_trades():
    positions = mt5.positions_get(symbol=SYMBOL)
    return len(positions) if positions else 0

# -------- PLACE TRADE --------
def place_trade(direction):
    global lot

    tick = mt5.symbol_info_tick(SYMBOL)

    if direction == "buy":
        price = tick.ask
        sl = price - SL_POINTS * 0.01
        tp = price + TP_POINTS * 0.01
        order_type = mt5.ORDER_TYPE_BUY
    else:
        price = tick.bid
        sl = price + SL_POINTS * 0.01
        tp = price - TP_POINTS * 0.01
        order_type = mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 999999,
        "comment": "Trend Scalper",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)

    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"🚀 {direction.upper()} {lot} lot @ {price}")
    else:
        print("❌ Trade failed:", result)

# -------- CLOSE FAST --------
def close_small_profit():
    positions = mt5.positions_get(symbol=SYMBOL)
    if positions:
        for pos in positions:
            if pos.profit > 0.5:
                close_trade(pos)

# -------- CLOSE TRADE --------
def close_trade(pos):
    tick = mt5.symbol_info_tick(SYMBOL)

    if pos.type == 0:
        price = tick.bid
        order_type = mt5.ORDER_TYPE_SELL
    else:
        price = tick.ask
        order_type = mt5.ORDER_TYPE_BUY

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": pos.volume,
        "type": order_type,
        "position": pos.ticket,
        "price": price,
        "deviation": 20,
        "magic": 999999,
    }

    mt5.order_send(request)
    print("💨 Closed profit")

# -------- MARTINGALE --------
def update_lot():
    global lot

    deals = mt5.history_deals_get(time.time() - 3600, time.time())

    if deals:
        last = deals[-1]

        if last.profit < 0:
            lot *= 1.5  # softer martingale (safer)
            print(f"⚠️ Martingale -> lot now {lot}")
        else:
            lot = BASE_LOT

# -------- MAIN LOOP --------
while True:
    df = get_data()
    latest = df.iloc[-1]

    price = latest['close']
    ema50 = latest['ema50']
    rsi = latest['rsi']

    print(f"Running... Price: {price:.2f} | RSI: {rsi:.2f} | Lot: {lot}")

    if count_trades() < MAX_TRADES:

        # 📈 UPTREND → ONLY BUY
        if price > ema50:
            if rsi < 50:
                place_trade("buy")

        # 📉 DOWNTREND → ONLY SELL
        elif price < ema50:
            if rsi > 50:
                place_trade("sell")

    close_small_profit()
    update_lot()

    time.sleep(1)
