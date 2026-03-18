def get_mt5_data():
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
                    "profit": real_profit
                })

    df = pd.DataFrame(data)

    if df.empty:
        return pd.DataFrame(columns=["date","profit","day","equity"])

    df['date'] = pd.to_datetime(df['date'])
    df['profit'] = pd.to_numeric(df['profit'])
    df['day'] = df['date'].dt.date
    df['equity'] = df['profit'].cumsum()

    return df
