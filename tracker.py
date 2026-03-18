from flask import Flask, jsonify, render_template
from flask_cors import CORS
import MetaTrader5 as mt5
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# ---------------- CONNECT ----------------
mt5.initialize()

# ---------------- GET TRADES ----------------
def get_trades():
    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)

    deals = mt5.history_deals_get(from_date, to_date)

    trades = []

    if deals:
        for d in deals:
            if d.type in [0, 1]:
                trades.append({
                    "symbol": d.symbol,
                    "type": "BUY" if d.type == 0 else "SELL",
                    "profit": d.profit,
                    "volume": d.volume,
                    "time": datetime.fromtimestamp(d.time).strftime("%Y-%m-%d %H:%M")
                })

    return trades

# ---------------- STATS ----------------
@app.route('/stats')
def stats():
    trades = get_trades()

    total = len(trades)
    wins = sum(1 for t in trades if t["profit"] > 0)
    losses = sum(1 for t in trades if t["profit"] < 0)
    profit = sum(t["profit"] for t in trades)

    winrate = (wins / total * 100) if total else 0

    return jsonify({
        "total": total,
        "wins": wins,
        "losses": losses,
        "profit": round(profit, 2),
        "winrate": round(winrate, 2)
    })

# ---------------- TRADES ----------------
@app.route('/trades')
def trades():
    return jsonify(get_trades())

# ---------------- DASHBOARD PAGE ----------------
@app.route('/')
def dashboard():
    return render_template("dashboard.html")

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
