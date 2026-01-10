import os
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

ETF_FILE = "etfs.csv"
LOG_FILE = "intraday_hits.csv"
THRESHOLD = -2.5

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def scan_etfs():
    etfs = pd.read_csv(ETF_FILE, header=None)[0].tolist()
    hits = []

    for symbol in etfs:
        try:
            data = yf.Ticker(symbol).history(period="2d", interval="1m")
            if data.empty or len(data) < 2:
                continue

            prev_close = data["Close"].iloc[-2]
            current_price = data["Close"].iloc[-1]
            pct_change = ((current_price - prev_close) / prev_close) * 100

            if pct_change <= THRESHOLD:
                hits.append((symbol, round(pct_change, 2)))

        except Exception:
            continue

    if hits:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        df = pd.DataFrame(hits, columns=["symbol", "pct_change"])
        df["time"] = now
        df.to_csv(LOG_FILE, mode="a", header=not os.path.exists(LOG_FILE), index=False)

        msg = "📉 ETF Drop Alert\n" + now + "\n\n" + "\n".join([f"{s}: {p}%" for s, p in hits])
        send_telegram(msg)

def send_daily_summary():
    today = datetime.now().strftime("%Y-%m-%d")

    if not os.path.exists(LOG_FILE):
        send_telegram(f"📊 Daily ETF Summary ({today})\n\nNo ETFs breached -2.5% today.")
        return

    df = pd.read_csv(LOG_FILE)
    unique_etfs = sorted(df["symbol"].unique().tolist())

    if unique_etfs:
        msg = f"📊 Daily ETF Summary ({today})\n\n" + "\n".join(unique_etfs)
    else:
        msg = f"📊 Daily ETF Summary ({today})\n\nNo ETFs breached -2.5% today."

    send_telegram(msg)

    # clear for next day
    os.remove(LOG_FILE)

if __name__ == "__main__":
    MODE = os.getenv("MODE", "SCAN")
    if MODE == "SUMMARY":
        send_daily_summary()
    else:
        scan_etfs()
