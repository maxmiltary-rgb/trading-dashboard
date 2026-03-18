import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="PnL Calendar", layout="wide")

# =========================
# BACKGROUND (MATCH DASHBOARD)
# =========================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 70% 20%, rgba(0, 140, 255, 0.25), transparent 40%),
                radial-gradient(circle at 30% 80%, rgba(0, 255, 150, 0.15), transparent 40%),
                #05070f !important;
}

[data-testid="stHeader"], [data-testid="stToolbar"] {
    background: transparent !important;
}

.card {
    background: rgba(15, 23, 42, 0.7);
    padding: 20px;
    border-radius: 18px;
    backdrop-filter: blur(12px);
}

.metric-title { color: #94a3b8; }
.metric-value { font-size: 26px; font-weight: bold; }

</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA (ERROR PROOF)
# =========================
df = pd.read_csv("trades.csv")
df.columns = df.columns.str.lower()

# auto handle date/time
if 'time' in df.columns:
    df['time'] = pd.to_datetime(df['time'])
elif 'date' in df.columns:
    df['time'] = pd.to_datetime(df['date'])
else:
    st.error("❌ No date/time column found in trades.csv")
    st.stop()

# profit
if 'profit' in df.columns:
    df['profit'] = pd.to_numeric(df['profit'])
else:
    st.error("❌ No profit column found")
    st.stop()

# =========================
# HEADER
# =========================
st.title("📅 PnL Calendar")

# =========================
# DAILY AGGREGATION
# =========================
df['day'] = df['time'].dt.date
daily = df.groupby('day')['profit'].sum().reset_index()

daily['day'] = pd.to_datetime(daily['day'])
daily['month'] = daily['day'].dt.month
daily['day_num'] = daily['day'].dt.day

# =========================
# 📅 HEATMAP (PRO STYLE)
# =========================
st.subheader("📊 Monthly Performance Heatmap")

fig = px.density_heatmap(
    daily,
    x="day_num",
    y="month",
    z="profit",
    color_continuous_scale="RdYlGn",
)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="white",
    coloraxis_colorbar=dict(title="PnL")
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# 🧠 INSIGHTS PANEL
# =========================
st.subheader("🧠 Performance Insights")

best_day = daily['profit'].max()
worst_day = daily['profit'].min()
avg_day = daily['profit'].mean()

col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div class="card">
<div class="metric-title">Best Day</div>
<div class="metric-value" style="color:#22c55e;">€{round(best_day,2)}</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="card">
<div class="metric-title">Worst Day</div>
<div class="metric-value" style="color:#ef4444;">€{round(worst_day,2)}</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="card">
<div class="metric-title">Average Day</div>
<div class="metric-value">€{round(avg_day,2)}</div>
</div>
""", unsafe_allow_html=True)

# =========================
# 🔥 STREAK TRACKER
# =========================
st.subheader("🔥 Streak Analysis")

daily['win'] = daily['profit'] > 0

streak = 0
max_streak = 0

for val in daily['win']:
    if val:
        streak += 1
        max_streak = max(max_streak, streak)
    else:
        streak = 0

st.write(f"🔥 Max Winning Streak: {max_streak} days")

# =========================
# TABLE
# =========================
with st.expander("📄 Daily Breakdown"):
    st.dataframe(daily)
