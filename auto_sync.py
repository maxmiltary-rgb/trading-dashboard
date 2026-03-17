import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import os
import time

# ---------- SETTINGS ----------
GITHUB_COMMIT_MSG = "auto update trades"

# ---------- EXPORT TRADES ----------
def export_trades():
    mt5.initialize()

    deals = mt5.history_deals_get(datetime(2025,1,1), datetime.now())

    data = []

    for d in deals:
        if d.entry == 1:
            time_trade = datetime.fromtimestamp(d.time)
            hour = time_trade.hour

            # Session detection
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
    df.to_csv("trades.csv", index=False)

    print("✅ trades.csv updated")


# ---------- PUSH TO GITHUB ----------
def push_to_github():
    os.system("git add .")
    os.system(f'git commit -m "{GITHUB_COMMIT_MSG}"')
    os.system("git push")
    print("🚀 pushed to GitHub")


# ---------- LOOP ----------
while True:
    try:
        export_trades()
        push_to_github()
    except Exception as e:
        print("❌ Error:", e)

    time.sleep(300)  # every 5 minutes