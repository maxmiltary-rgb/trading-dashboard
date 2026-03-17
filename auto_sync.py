import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import os
import time

# ---------- EXPORT ----------
def export_trades():
    mt5.initialize()

    deals = mt5.history_deals_get(datetime(2025,1,1), datetime.now())

    data = []

    for d in deals:
        if d.entry == 1:
            time_trade = datetime.fromtimestamp(d.time)
            hour = time_trade.hour

            if 7 <= hour < 13:
                session = "London"
            elif 13 <= hour < 21:
                session = "New York"
            else:
                session = "Asia"

            rr = abs(d.profit) / (d.volume * 10) if d.volume else 0

            data.append({
                "date": time_trade,
                "profit": d.profit,
                "symbol": d.symbol,
                "rr": rr,
                "session": session
            })

    df = pd.DataFrame(data)

    # 🔥 FORCE CHANGE (timestamp column)
    df["last_update"] = datetime.now()

    df.to_csv("trades.csv", index=False)

    print("✅ trades.csv updated")


# ---------- PUSH ----------
def push_to_github():
    os.system("git add .")

    status = os.popen("git status --porcelain").read()

    if status.strip() == "":
        print("⚠️ No changes")
        return

    os.system('git commit -m "auto update trades"')
    os.system("git push")

    print("🚀 pushed to GitHub")


# ---------- LOOP ----------
while True:
    try:
        export_trades()
        push_to_github()
    except Exception as e:
        print("❌ Error:", e)

    time.sleep(300)
