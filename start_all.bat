cd /d "C:\Users\maxmi\OneDrive\Documents\Trading"

start cmd /k python tracker.py
timeout /t 3
start cmd /k python xau_sniper_bot.py
start cmd /k python telegram_copier.py