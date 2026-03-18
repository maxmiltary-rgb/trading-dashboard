import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import time
import subprocess

mt5.initialize()

while True:
    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)

    deals = mt5.history_deals_get(from_date, to_date)

    data = []

    if deals:
        for d in deals:
            if d.type in [0, 1]:
                data.append({
                    "date": datetime.fromtimestamp(d.time),
                    "profit": d.profit,
                    "symbol": d.symbol,
                    "type": "BUY" if d.type == 0 else "SELL",
                    "volume": d.volume
                })

    df = pd.DataFrame(data)

    if not df.empty:
        df.to_csv("trades.csv", index=False)
        print("✅ Updated trades.csv")

        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "auto update"])
        subprocess.run(["git", "push"])

    time.sleep(10)  # update every 10 seconds
