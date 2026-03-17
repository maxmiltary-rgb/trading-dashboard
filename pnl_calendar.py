import pandas as pd
import calendar
from datetime import datetime
import matplotlib.pyplot as plt

# Load trades
df = pd.read_csv("trades.csv")

# Convert date
df['date'] = pd.to_datetime(df['date'])

# Group by day
daily = df.groupby(df['date'].dt.date)['profit'].sum()

# Select month
year = datetime.now().year
month = datetime.now().month

cal = calendar.monthcalendar(year, month)

fig, ax = plt.subplots(figsize=(10, 6))

for i, week in enumerate(cal):
    for j, day in enumerate(week):
        if day != 0:
            date = datetime(year, month, day).date()
            pnl = daily.get(date, 0)

            color = "green" if pnl > 0 else "red" if pnl < 0 else "gray"

            ax.text(j, -i, f"{day}\n{round(pnl,2)}€",
                    ha='center', va='center',
                    bbox=dict(facecolor=color, alpha=0.6))

ax.set_xlim(-0.5, 6.5)
ax.set_ylim(-len(cal), 0.5)
ax.axis('off')

plt.title(f"PnL Calendar {month}/{year}")
plt.show()