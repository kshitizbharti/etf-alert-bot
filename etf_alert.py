import os
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

ETF_FILE = "etfs.csv"
THRESHOLD = -2.5

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def scan_etfs(title):
    etfs = pd.read_csv(ETF_FILE, header=None)[0].tolist()
    hits = []

    for symbol in etfs:
        try:
            data = yf.Ticker(symbol).history(period="2d", interval="1m")
            if data.empty or len(data) < 2:
                continue

            prev_close = data["Close"].iloc[-2]
            current_price = data["Close"].iloc[-1]
            pct = ((current_price - prev_close) / prev_close) * 100

            if pct <= THRESHOLD:
                hits.append(f"{symbol} : {pct:.2f}%")

        except Exception:
            continue

    if hits:
        now = datetime.now().strftime("%d-%m-%Y %H:%M")
        msg = f"{title}\n{now}\n\n" + "\n".join(hits)
        send_telegram(msg)

def eod_summary():
    etfs = pd.read_csv(ETF_FILE, header=None)[0].tolist()
    hits = []

    for symbol in etfs:
        try:
            data = yf.Ticker(symbol).history(period="2d", interval="1m")
            if data.empty or len(data) < 2:
                continue

            prev_close = data["Close"].iloc[-2]
            close_price = data["Close"].iloc[-1]
            pct = ((close_price - prev_close) / prev_close) * 100

            if pct <= THRESHOLD:
                hits.append(f"{symbol} : {pct:.2f}%")

        except Exception:
            continue

    today = datetime.now().strftime("%d-%m-%Y")
    if hits:
        msg = f"📊 EOD ETF Summary ({today})\n\n" + "\n".join(hits)
    else:
        msg = f"📊 EOD ETF Summary ({today})\n\nNo ETF closed below -2.5%."

    send_telegram(msg)

def test_ping():
    now = datetime.now().strftime("%H:%M:%S")
    send_telegram(f"🧪 Test ping at {now}")

if __name__ == "__main__":
    MODE = os.getenv("MODE", "SCAN")

    if MODE == "INTRADAY":
        scan_etfs("📉 Intraday ETF Alert")
    elif MODE == "EOD":
        eod_summary()
    elif MODE == "TEST":
        test_ping()

