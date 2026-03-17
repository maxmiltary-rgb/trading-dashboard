import time
import os

while True:
    os.system("python trade_logger.py")
    os.system("python pnl_calendar.py")
    time.sleep(300)  # update every 5 min