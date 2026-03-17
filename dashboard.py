import streamlit as st
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import calendar
import plotly.graph_objects as go
import requests

st.set_page_config(layout="wide")

# ---------- TELEGRAM ----------
BOT_TOKEN = ""
CHAT_ID = ""

def send_alert(message):
    if BOT_TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": message})

# ---------- STYLE ----------
st.markdown("""
<style>
.stApp { background-color: #0e1117; color: white; }
#MainMenu, footer, header {visibility: hidden;}

.metric-box {
    background: linear-gradient(145deg, #111827, #1f2937);
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 10px;
}

.day-card {
    border-radius: 12px;
    padding: 10px;
    font-weight: 500;
    height: 85px;
    transition: 0.2s;
}

.green { background: #16c784; }
.red { background: #ea3943; }
.gray { background: #2a2e39; }

.day-card:hover {
    transform: scale(1.05);
}

.small { font-size: 11px; opacity: 0.8; }
.big { font-size: 15px; font-weight: bold; }

</style>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.title("⚙️ Filters")

symbol_filter = st.sidebar.multiselect(
    "Symbol",
    options=["XAUUSD", "EURUSD", "GBPUSD"],
    default=["XAUUSD"]
)

session_filter = st.sidebar.multiselect(
    "Session",
    options=["London", "New York", "Asia"],
    default=["London", "New York"]
)

# ---------- MT5 ----------
if not mt5.initialize():
    st.error("MT5 connection failed")
    st.stop()

deals = mt5.history_deals_get(datetime(2025,1,1), datetime.now())

data = []
for d in deals:
    if d.entry == 1:
        hour = datetime.fromtimestamp(d.time).hour

        # Session detection
        if 7 <= hour < 13:
            session = "London"
        elif 13 <= hour < 21:
            session = "New York"
        else:
            session = "Asia"

        data.append({
            "date": datetime.fromtimestamp(d.time),
            "profit": d.profit,
            "symbol": d.symbol,
            "rr": abs(d.profit / d.volume) if d.volume else 0,
            "session": session
        })

df = pd.DataFrame(data)

if df.empty:
    st.warning("No trades found")
    st.stop()

df['date_only'] = df['date'].dt.date

# ---------- APPLY FILTERS ----------
df = df[df['symbol'].isin(symbol_filter)]
df = df[df['session'].isin(session_filter)]

# ---------- DAILY ----------
daily = df.groupby('date_only').agg(
    pnl=('profit','sum'),
    trades=('profit','count'),
    win_rate=('profit', lambda x: (x > 0).mean()),
    avg_rr=('rr','mean')
).reset_index()

# ---------- MOBILE STYLE HEADER ----------
st.markdown("## 📊 PnL Overview")

col1, col2, col3 = st.columns(3)
col1.metric("Total", f"{df['profit'].sum():.2f}€")
col2.metric("Trades", len(df))
col3.metric("Win Rate", f"{(df['profit']>0).mean()*100:.1f}%")

st.divider()

# ---------- EQUITY ----------
fig = go.Figure()
df_sorted = df.sort_values('date')
df_sorted['equity'] = df_sorted['profit'].cumsum()

fig.add_trace(go.Scatter(x=df_sorted['date'], y=df_sorted['equity']))
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------- CLICK STATE ----------
if "selected_day" not in st.session_state:
    st.session_state.selected_day = None

# ---------- CALENDAR ----------
year = datetime.now().year
month = datetime.now().month
cal = calendar.monthcalendar(year, month)

days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
cols = st.columns(7)

for i, d in enumerate(days):
    cols[i].markdown(f"**{d}**")

for week in cal:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].write("")
        else:
            date = datetime(year, month, day).date()
            row = daily[daily['date_only'] == date]

            pnl = row['pnl'].values[0] if not row.empty else 0
            trades = row['trades'].values[0] if not row.empty else 0

            cls = "green" if pnl > 0 else "red" if pnl < 0 else "gray"

            cols[i].markdown(f"""
            <div class="day-card {cls}">
                <div class="small">{day}</div>
                <div class="big">{pnl:.2f}€</div>
                <div class="small">{trades} trades</div>
            </div>
            """, unsafe_allow_html=True)

            if cols[i].button(" ", key=str(date)):
                st.session_state.selected_day = date

# ---------- CLICK DAY ----------
if st.session_state.selected_day:
    st.divider()
    st.subheader(f"Trades on {st.session_state.selected_day}")

    day_trades = df[df['date_only'] == st.session_state.selected_day]
    st.dataframe(day_trades)

    trade_count = len(day_trades)
    pnl = day_trades['profit'].sum()

    if trade_count > 3:
        st.error("⚠️ Overtrading detected")
        send_alert("⚠️ Overtrading detected")

    if pnl < 0 and trade_count >= 3:
        st.error("⚠️ Revenge trading detected")
        send_alert("⚠️ Revenge trading detected")
