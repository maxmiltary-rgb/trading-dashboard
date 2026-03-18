import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import calendar

st.set_page_config(page_title="Trading Dashboard", layout="wide")

# =========================
# 🎨 PRO DARK BLUE THEME
# =========================
st.markdown("""
<style>

/* BACKGROUND */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0b1e2d, #0f2a3f);
}

/* REMOVE STREAMLIT UI */
#MainMenu, footer, header {visibility: hidden;}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #0a1926;
}

/* CARDS */
.card {
    background: linear-gradient(145deg, #0f2a3f, #0b1e2d);
    padding: 20px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.05);
}

/* TEXT */
.metric-title {
    color: #9ca3af;
    font-size: 13px;
}

.metric-value {
    font-size: 28px;
    font-weight: 600;
    color: white;
}

/* COLORS */
.green { color: #22c55e; }
.red { color: #ef4444; }

/* CALENDAR */
.day-box {
    border-radius: 10px;
    padding: 10px;
    height: 75px;
    color: white;
}

.pos { background-color: #14532d; }
.neg { background-color: #7f1d1d; }

.header-day {
    text-align: center;
    color: #9ca3af;
    font-size: 13px;
}

/* TABLE */
[data-testid="stDataFrame"] {
    background-color: #0b1e2d;
}

/* BUTTONS */
.stButton>button {
    background-color: #1f6feb;
    color: white;
    border-radius: 6px;
    border: none;
}

</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("trades.csv")
df['date'] = pd.to_datetime(df['date'])
df['profit'] = pd.to_numeric(df['profit'])
df['day'] = df['date'].dt.date

# =========================
# CALCULATIONS
# =========================
total_pnl = df['profit'].sum()
total_trades = len(df)
wins = df[df['profit'] > 0].shape[0]
losses = df[df['profit'] < 0].shape[0]
winrate = (wins / total_trades * 100) if total_trades else 0

df['equity'] = df['profit'].cumsum()
daily = df.groupby('day')['profit'].sum()

# =========================
# SIDEBAR NAV
# =========================
page = st.sidebar.radio("Menu", ["Dashboard", "Journal"])

# =========================
# 📊 DASHBOARD
# =========================
if page == "Dashboard":

    st.title("Dashboard")

    # =========================
    # OBJECTIVES ROW
    # =========================
    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(f"""
    <div class="card">
    <div class="metric-title">Profit</div>
    <div class="metric-value green">€{round(total_pnl,2)}</div>
    </div>
    """, unsafe_allow_html=True)

    c2.markdown(f"""
    <div class="card">
    <div class="metric-title">Win Rate</div>
    <div class="metric-value">{round(winrate,1)}%</div>
    </div>
    """, unsafe_allow_html=True)

    c3.markdown(f"""
    <div class="card">
    <div class="metric-title">Wins</div>
    <div class="metric-value green">{wins}</div>
    </div>
    """, unsafe_allow_html=True)

    c4.markdown(f"""
    <div class="card">
    <div class="metric-title">Losses</div>
    <div class="metric-value red">{losses}</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # =========================
    # EQUITY + STATS
    # =========================
    left, right = st.columns([2,1])

    # EQUITY
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['equity'],
            mode='lines',
            line=dict(color='#22c55e', width=2)
        ))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0,r=0,t=20,b=0)
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # STATS
    with right:
        st.markdown(f"""
        <div class="card">
        <div class="metric-title">Avg Trade</div>
        <div class="metric-value">€{round(df['profit'].mean(),2)}</div>
        <br>
        <div class="metric-title">Best Day</div>
        <div class="metric-value green">€{round(daily.max(),2)}</div>
        <br>
        <div class="metric-title">Worst Day</div>
        <div class="metric-value red">€{round(daily.min(),2)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # =========================
    # 📅 CALENDAR
    # =========================
    st.subheader("PnL Calendar")

    year = datetime.now().year
    month = datetime.now().month
    cal = calendar.monthcalendar(year, month)

    if "selected_day" not in st.session_state:
        st.session_state.selected_day = None

    day_names = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

    header = st.columns(7)
    for i, d in enumerate(day_names):
        header[i].markdown(f"<div class='header-day'>{d}</div>", unsafe_allow_html=True)

    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                date = datetime(year, month, day).date()
                pnl = daily.get(date, 0)

                cls = "pos" if pnl > 0 else "neg" if pnl < 0 else ""

                cols[i].markdown(f"""
                <div class="day-box {cls}">
                    €{round(pnl,2)}
                </div>
                """, unsafe_allow_html=True)

                if cols[i].button(str(day), key=f"btn_{date}"):
                    st.session_state.selected_day = date

    # CLICK DETAILS
    if st.session_state.selected_day:
        st.divider()
        st.subheader(f"Trades on {st.session_state.selected_day}")
        st.dataframe(df[df['day'] == st.session_state.selected_day], use_container_width=True)

# =========================
# 📄 JOURNAL PAGE
# =========================
if page == "Journal":

    st.title("Trading Journal")

    st.dataframe(df, use_container_width=True)

    st.divider()

    st.subheader("Performance")

    st.write(f"Total Trades: {total_trades}")
    st.write(f"Win Rate: {round(winrate,1)}%")
    st.write(f"Total Profit: €{round(total_pnl,2)}")
