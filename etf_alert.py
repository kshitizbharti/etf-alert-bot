import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


ETF_FILE = "etfs.csv"
THRESHOLD = -2.5

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def main():
    etfs = pd.read_csv(ETF_FILE, header=None)[0].tolist()
    alerts = []

    for symbol in etfs:
        try:
            data = yf.Ticker(symbol).history(period="2d", interval="1m")
            if data.empty or len(data) < 2:
                continue

            prev_close = data["Close"].iloc[-2]
            current_price = data["Close"].iloc[-1]
            pct_change = ((current_price - prev_close) / prev_close) * 100

            if pct_change <= THRESHOLD:
                alerts.append(f"{symbol}: {pct_change:.2f}%")

        except Exception:
            continue

    now = datetime.now().strftime("%d-%m-%Y %H:%M")

    if alerts:
        message = "📉 ETF Drop Alert\n" + now + "\n\n" + "\n".join(alerts)
    else:
        message = "ℹ️ ETF scan completed.\n" + now + "\n\nNo ETFs breached -2.5%."

    send_telegram(message)

if __name__ == "__main__":
    main()
