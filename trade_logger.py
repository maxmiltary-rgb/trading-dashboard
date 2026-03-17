import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import os

# Connect to MT5
mt5.initialize()

# Get closed trades
deals = mt5.history_deals_get(datetime(2025,1,1), datetime.now())

data = []

for d in deals:
    if d.entry == 1:  # closed trades only
        data.append({
            "date": datetime.fromtimestamp(d.time).strftime("%Y-%m-%d"),
            "profit": d.profit,
            "symbol": d.symbol,
            "volume": d.volume,
        })

df = pd.DataFrame(data)

# Save to CSV (your database)
df.to_csv("trades.csv", index=False)

print("✅ Trades updated")