import requests
import time
import json
import os
from datetime import datetime
from telegram import Bot

# ---------- CONFIGURATION ----------
TELEGRAM_TOKEN = "8753448870:AAEIVpLosykpT_x5FRfqOElBPZohj7w2cAc"   
CHAT_ID = "6226335310"            
# -----------------------------------

bot = Bot(token=TELEGRAM_TOKEN)

# File to store last seen delisted symbols
DATA_FILE = "delisted_cache.json"

def load_previous_delistings():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_current_delistings(delist_set):
    with open(DATA_FILE, "w") as f:
        json.dump(list(delist_set), f)

def fetch_binance_delist_schedule():
    """
    Binance official endpoint for spot delisting schedule.
    No API key required.
    """
    url = "https://api.binance.com/sapi/v1/spot/delist-schedule"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # data is list of objects like: { "symbol": "XXX", "delistTime": 123456789 }
        symbols = [item["symbol"] for item in data if "symbol" in item]
        return set(symbols)
    except Exception as e:
        print(f"[ERROR] Failed to fetch delist schedule: {e}")
        return None

def send_telegram_alert(new_symbols):
    message = f"⚠️ *Binance Delisting Alert*\n\nNewly scheduled delistings:\n{', '.join(new_symbols)}\n\nCheck Binance announcement for details."
    try:
        bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
        print(f"[ALERT SENT] {datetime.now()} - {new_symbols}")
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")

def main_loop():
    print(f"[START] Monitoring Binance delistings. Time: {datetime.now()}")
    previous = load_previous_delistings()
    print(f"Previously cached delistings: {previous if previous else 'None'}")

    while True:
        current = fetch_binance_delist_schedule()
        if current is not None:
            new_delistings = current - previous
            if new_delistings:
                send_telegram_alert(new_delistings)
                # Update cache
                previous = current
                save_current_delistings(previous)
            else:
                print(f"[CHECK] {datetime.now()} - No new delistings")
        else:
            print(f"[RETRY] {datetime.now()} - API failed, will retry after 30 min")

        # Wait 30 minutes before next check
        time.sleep(30 * 60)

if __name__ == "__main__":
    main_loop()
