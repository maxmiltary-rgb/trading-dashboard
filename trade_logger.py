import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

mt5.initialize()

deals = mt5.history_deals_get(datetime(2025,1,1), datetime.now())

data = []

for d in deals:
    if d.entry == 1:  # closed trades only

        time = datetime.fromtimestamp(d.time)
        hour = time.hour

        # Session detection (Germany time)
        if 7 <= hour < 13:
            session = "London"
        elif 13 <= hour < 21:
            session = "New York"
        else:
            session = "Asia"

        # RR calculation (better approximation)
        rr = 0
        if d.volume > 0:
            rr = abs(d.profit) / (d.volume * 10)

        data.append({
            "date": time,
            "profit": d.profit,
            "symbol": d.symbol,
            "rr": rr,
            "session": session
        })

df = pd.DataFrame(data)

df.to_csv("trades.csv", index=False)

print("✅ trades.csv updated correctly")
