import MetaTrader5 as mt5
import pandas as pd
import time
import requests
from datetime import datetime

# ---------------- SETTINGS ----------------
SYMBOL = "XAUUSD"  # change if needed
RISK_PERCENT = 10
MAX_DAILY_LOSS_PERCENT = 30

current_day = datetime.now().day
start_balance = None

# ---------------- CONNECT ----------------
if not mt5.initialize():
    print("MT5 connection failed")
    quit()
else:
    print("Connected to MT5")

# ---------------- FUNCTIONS ----------------

def send_to_dashboard(direction, lot, entry, sl, tp):
    url = "http://127.0.0.1:5000/new_trade"

    data = {
        "symbol": SYMBOL,
        "type": direction,
        "lot": lot,
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "time": str(datetime.now())
    }

    try:
        requests.post(url, json=data)
        print("📡 Sent to dashboard ✅")
    except:
        print("❌ Failed to send to dashboard")

def get_data(tf, bars=200):
    rates = mt5.copy_rates_from_pos(SYMBOL, tf, 0, bars)
    return pd.DataFrame(rates)

def get_trend():
    df = get_data(mt5.TIMEFRAME_H4)
    df['ma'] = df['close'].rolling(100).mean()
    return "buy" if df['close'].iloc[-1] > df['ma'].iloc[-1] else "sell"

def get_zone():
    df = get_data(mt5.TIMEFRAME_H1)
    high = df['high'].rolling(20).max().iloc[-1]
    low = df['low'].rolling(20).min().iloc[-1]
    price = df['close'].iloc[-1]

    if abs(price - high) < 5:
        return ("sell", high)
    if abs(price - low) < 5:
        return ("buy", low)

    return None

def detect_bos():
    df = get_data(mt5.TIMEFRAME_M15)

    if df['close'].iloc[-1] > df['high'].rolling(20).max().iloc[-2]:
        return "buy"
    if df['close'].iloc[-1] < df['low'].rolling(20).min().iloc[-2]:
        return "sell"

    return None

def entry_confirmation(direction):
    df = get_data(mt5.TIMEFRAME_M5)
    last = df['close'].iloc[-2]
    prev = df['close'].iloc[-3]

    return last > prev if direction == "buy" else last < prev

def is_trading_session():
    hour = datetime.now().hour
    return 8 <= hour < 22

def calculate_lot(sl_points):
    balance = mt5.account_info().balance
    risk_amount = balance * (RISK_PERCENT / 100)
    pip_value = 0.1
    lot = risk_amount / (sl_points * pip_value)
    return round(max(0.01, min(lot, 5)), 2)

def hit_daily_loss():
    global start_balance
    balance = mt5.account_info().balance

    if start_balance is None:
        start_balance = balance

    loss = (start_balance - balance) / start_balance * 100
    return loss >= MAX_DAILY_LOSS_PERCENT

def place_trade(direction, sl, tp, lot):
    tick = mt5.symbol_info_tick(SYMBOL)
    price = tick.ask if direction == "buy" else tick.bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY if direction == "buy" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 777,
        "comment": "SNIPER V3",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    print("📈 ORDER:", result)
    return price

# ---------------- MAIN LOOP ----------------

while True:
    print("\n🤖 Bot running...")

    now = datetime.now()

    # reset daily loss tracker
    if now.day != current_day:
        current_day = now.day
        start_balance = None

    if not is_trading_session():
        print("⏰ Outside trading hours")
        time.sleep(60)
        continue

    if hit_daily_loss():
        print("🛑 Daily loss limit reached")
        time.sleep(300)
        continue

    trend = get_trend()
    zone = get_zone()
    bos = detect_bos()

    print(f"Trend: {trend} | Zone: {zone} | BOS: {bos}")

    if zone and bos:
        direction, level = zone

        if direction == trend and direction == bos:

            if entry_confirmation(direction):
                print("🎯 Sniper entry confirmed")

                tick = mt5.symbol_info_tick(SYMBOL)
                price = tick.ask if direction == "buy" else tick.bid

                if direction == "buy":
                    sl = level - 2
                    tp = price + (price - sl) * 2
                    sl_points = abs(price - sl)
                else:
                    sl = level + 2
                    tp = price - (sl - price) * 2
                    sl_points = abs(sl - price)

                lot = calculate_lot(sl_points)

                print(f"💰 Lot size: {lot}")

                entry_price = place_trade(direction, sl, tp, lot)

                send_to_dashboard(direction, lot, entry_price, sl, tp)

                time.sleep(300)

    time.sleep(10)
