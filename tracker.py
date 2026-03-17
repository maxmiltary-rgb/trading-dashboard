from flask import Flask, jsonify
from flask_cors import CORS
import MetaTrader5 as mt5
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

mt5.initialize()

@app.route("/stats")
def stats():
    from_date = datetime.now() - timedelta(days=30)
    deals = mt5.history_deals_get(from_date, datetime.now())
    positions = mt5.positions_get()

    total = 0
    wins = 0
    profit = 0
    equity = []
    running = 0
    history = []

    if deals:
        for d in deals:
            if d.entry == 1:
                total += 1
                profit += d.profit
                running += d.profit
                equity.append(running)

                history.append({
                    "symbol": d.symbol,
                    "profit": round(d.profit, 2),
                    "type": "BUY" if d.type == 0 else "SELL",
                    "time": datetime.fromtimestamp(d.time).strftime("%d %b %H:%M")
                })

                if d.profit > 0:
                    wins += 1

    if positions:
        for p in positions:
            history.insert(0, {
                "symbol": p.symbol,
                "profit": round(p.profit, 2),
                "type": "BUY" if p.type == 0 else "SELL",
                "time": "OPEN"
            })

    winrate = (wins / total * 100) if total > 0 else 0

    return jsonify({
        "total_trades": total,
        "winrate": round(winrate, 2),
        "profit": round(profit, 2),
        "equity": equity,
        "history": history
    })

app.run(host="0.0.0.0", port=5000)
