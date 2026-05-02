import feedparser
import time
import json
import os
import requests
from datetime import datetime

# ---------- CONFIGURATION ----------
TELEGRAM_TOKEN = "8753455dw"
CHAT_ID = "15215415"

# ---------- BUTTON CONFIGURATION ----------
CHANNEL_USERNAME = "udbannerpvt"   # <-- Change this
DEV_USERNAME = "udbanner"               # <-- Change this
# -------------------------------------------

def send_telegram_message(text, buttons=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    if buttons:
        payload["reply_markup"] = json.dumps({"inline_keyboard": buttons})
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.json()
    except Exception as e:
        print(f"Telegram send error: {e}")
        return None

def get_buttons():
    """Returns the two buttons for Join Channel and Contact Developer"""
    return [
        [
            {"text": "🔊 Join Channel", "url": f"https://t.me/{CHANNEL_USERNAME}"},
            {"text": "👨‍💻 Contact Developer", "url": f"https://t.me/{DEV_USERNAME}"}
        ]
    ]

def send_test_message():
    result = send_telegram_message(
        "🧪 *Test Alert*: Your Binance delisting bot is active and working!",
        buttons=get_buttons()   # <-- Buttons added here
    )
    if result and result.get("ok"):
        print("Test message with buttons sent to Telegram!")
    else:
        print(f"Test message failed: {result}")

DATA_FILE = "delist_rss_cache.json"

def load_sent_guids():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_sent_guids(guid_set):
    with open(DATA_FILE, "w") as f:
        json.dump(list(guid_set), f)

def check_binance_rss():
    url = "https://www.binance.com/en/support/announcement/rss?catalog=48"
    try:
        feed = feedparser.parse(url)
        sent_guids = load_sent_guids()
        new_entries = []
        for entry in feed.entries:
            guid = entry.get('guid', entry.get('id', ''))
            if guid and guid not in sent_guids:
                title = entry.get('title', '')
                if 'delist' in title.lower():
                    new_entries.append({
                        'guid': guid,
                        'title': title,
                        'link': entry.get('link', ''),
                        'published': entry.get('published', '')
                    })
        if new_entries:
            for entry in new_entries:
                message = f"⚠️ *Binance Delisting Alert*\n\n📌 {entry['title']}\n📅 {entry['published']}\n🔗 [Read More]({entry['link']})"
                # Send alert with same buttons
                send_telegram_message(message, buttons=get_buttons())
                sent_guids.add(entry['guid'])
                print(f"[ALERT] {datetime.now()} - {entry['title']}")
            save_sent_guids(sent_guids)
        else:
            print(f"[CHECK] {datetime.now()} - No new delisting announcements")
    except Exception as e:
        print(f"[ERROR] RSS fetch failed: {e}")

def main_loop():
    print(f"[START] Monitoring Binance Delisting RSS feed at {datetime.now()}")
    send_test_message()   # <-- Test message with buttons on startup
    while True:
        check_binance_rss()
        time.sleep(300)

if __name__ == "__main__":
    main_loop()
