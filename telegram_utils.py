import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

# Telegram Bot Token and Chat ID
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_BOT_USER_NAME = os.getenv("TELEGRAM_BOT_USER_NAME")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_GROUP_CHAT_ID = os.getenv("TELEGRAM_GROUP_CHAT_ID")

# tmp_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
# tmp = requests.get(tmp_url).json()


def send_telegram_message(message, chat_id):
    """Sends a message to the Telegram chat using the bot."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID or not TELEGRAM_GROUP_CHAT_ID:
        logging.error("Telegram bot token or chat ID is missing. Skipping notification.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        response_json = response.json()

        if response.status_code != 200 or not response_json.get("ok", False):
            error_description = response_json.get("description", "Unknown error")
            error_code = response_json.get("error_code", "No error code")

            if error_code == 400 and "not enough rights" in error_description.lower():
                logging.error(
                    "ERROR - Bot lacks permissions to send messages to the chat. Please check bot permissions.")
            else:
                logging.error(f"Failed to send Telegram message: {response_json}")
    except requests.RequestException as e:
        logging.error(f"Network error while sending Telegram message: {e}")
    except Exception as e:
        logging.error(f"Unexpected error sending Telegram message: {e}")
