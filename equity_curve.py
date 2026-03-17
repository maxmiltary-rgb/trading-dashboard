import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("trades.csv")
df['date'] = pd.to_datetime(df['date'])

df = df.sort_values('date')

df['equity'] = df['profit'].cumsum()

plt.plot(df['date'], df['equity'])
plt.title("Equity Curve")
plt.xlabel("Date")
plt.ylabel("Profit (€)")
plt.grid()

plt.show()