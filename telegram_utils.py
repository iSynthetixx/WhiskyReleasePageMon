import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

# Telegram Bot Token and Chat ID
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_BOT_USER_NAME = os.getenv("TELEGRAM_BOT_USER_NAME")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# tmp_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
# tmp = requests.get(tmp_url).json()


def send_telegram_message(message):
    """Sends a message to the Telegram chat using the bot."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("Telegram bot token or chat ID is missing. Skipping notification.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logging.error(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        logging.error(f"Error sending Telegram message: {e}")
