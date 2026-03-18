print(len(data))

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

            # ✅ ONLY CLOSED TRADES
            if d.entry == 1:  

                # ✅ REAL PROFIT (matches MT5)
                real_profit = d.profit + d.commission + d.swap

                data.append({
                    "date": datetime.fromtimestamp(d.time),
                    "profit": real_profit,
                    "symbol": d.symbol,
                    "type": "BUY" if d.type == 0 else "SELL",
                    "volume": d.volume
                })

    df = pd.DataFrame(data)

    if not df.empty:
        df.to_csv("trades.csv", index=False)
        print("✅ Updated trades.csv (REAL MT5 DATA)")

        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "auto update"])
        subprocess.run(["git", "push"])

    time.sleep(10)
