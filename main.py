import tls_client
import os
from dotenv import load_dotenv
import logging
import colorlog
from logging.handlers import RotatingFileHandler
import time
import requests
from db import *
from telegram import Bot

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
PRODUCT_URL = os.getenv("PRODUCT_URL")
CATEGORY_ID = os.getenv("CATEGORY_ID")
ITEM_QUERY_LIMIT = os.getenv("ITEM_QUERY_LIMIT")

# Ensure the item limit is an integer
try:
    ITEM_QUERY_LIMIT = int(ITEM_QUERY_LIMIT)
except ValueError:
    logging.error(f"Invalid ITEM_QUERY_LIMIT value: {ITEM_QUERY_LIMIT}. It should be an integer.")
    # Set a default value in case of error
    ITEM_QUERY_LIMIT = 250

STOCK_URL = os.getenv("STOCK_URL")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH")
PROXY_FILE_PATH = os.getenv("PROXY_FILE_PATH")

EXPECTED_PRODUCT_KEYS = {
    "id": "Unknown", "brand": "Unknown", "active": "Unknown", "displayName": "Unknown",
    "primaryFullImageURL": "Unknown", "b2c_highlyAllocatedProduct": None,
    "x_volume": "Unknown", "listPrice": "Unknown",
    "onlineOnly": "Unknown", "creationDate": "Unknown", "b2c_onlineAvailable": "Unknown",
    "b2c_onlineExclusive": "Unknown", "lastModifiedDate": "Unknown", "b2c_size": "Unknown",
    "b2c_proof": "Unknown", "b2c_futuresProduct": "Unknown", "b2c_comingSoon": "Unknown",
    "repositoryId": "Unknown", "b2c_type": "Unknown"
}

EXPECTED_STOCK_KEYS = {
    "preOrderableQuantity": "Unknown",
    "orderableQuantity": "Unknown", "stockStatus": "Unknown", "availabilityDate": "Unknown", "backOrderableQuantity": "Unknown",
    "inStockQuantity": "Unknown"
}

# Initialize the Telegram Bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def initialize_logging():
    """Configures the logging setup to log to both console and file with rotation."""
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    log_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red"
        }
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    file_handler = RotatingFileHandler(
        LOG_FILE_PATH, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(log_formatter)
    logging.basicConfig(level=logging.INFO, handlers=[console_handler, file_handler])

def handle_proxies(file_path):
    """Handles loading, validating, and saving proxies."""
    valid_proxies = []

    # Load proxies from the file
    try:
        with open(file_path, 'r') as f:
            proxies = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        logging.error(f"Proxy file {file_path} not found.")
        return []

    # Validate each proxy
    for proxy in proxies:
        try:
            response = requests.get('https://httpbin.org/ip', proxies={"http": proxy, "https": proxy}, timeout=10)
            if response.status_code == 200:
                valid_proxies.append(proxy)
            else:
                logging.warning(f"Proxy {proxy} failed with status code {response.status_code}")
        except requests.RequestException as e:
            logging.error(f"Error with proxy {proxy}: {e}")

    # Save only the valid proxies back to the file
    with open(file_path, 'w') as f:
        for proxy in valid_proxies:
            f.write(f"{proxy}\n")

    logging.info(f"Proxy file updated. {len(valid_proxies)} valid proxies remaining.")

    return valid_proxies

def create_session():
    """Creates a session with TLS client and configures proxy if available."""
    session = tls_client.Session(client_identifier="chrome_120", random_tls_extension_order=True)

    if not PROXY_FILE_PATH:
        logging.debug("PROXY_FILE environment variable is not set. Running without a proxy.")
        return session

    proxies = handle_proxies(PROXY_FILE_PATH)

    if proxies:
        session.proxies.update({"http": proxies[0], "https": proxies[0]})
        logging.info(f"Using proxy: {proxies[0]}")
    else:
        logging.debug("No valid proxies found. Running without a proxy.")

    return session

def _fetch_json(session, url, retries, max_retries, delay, backoff_factor):
    """Fetch and return JSON response with retry handling."""
    while retries < max_retries:
        try:
            resp = session.get(url)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code in {503, 429}:  # Retry on service unavailable or rate limit
                logging.warning(f"Retrying {url} due to {resp.status_code} (Attempt {retries+1})")
            elif resp.status_code == 403:
                logging.error("Access forbidden (403). Check your proxy settings or permissions.")
                return None
            else:
                logging.error(f"Unexpected status code {resp.status_code}. Retrying...")
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            logging.error(f"{type(e).__name__} while accessing {url}. Retrying...")

        retries += 1
        time.sleep(delay)
        delay *= backoff_factor  # Exponential backoff

    logging.error(f"Max retries reached for {url}.")
    return None

def product_api_request(session: tls_client.Session, product_url: str, category_id: str, item_limit: int,
                        offset: int = 0, max_retries: int = 3, delay: int = 5, backoff_factor: int = 2):
    """Fetch and validate product data with retry logic and return a dictionary where the key is the product id."""

    # Initialize an empty dictionary
    product_data = {}

    while True:
        search_url = f"{product_url}{category_id}&limit={item_limit}&offset={offset}"
        json_data = _fetch_json(session, search_url, retries=0, max_retries=max_retries, delay=delay, backoff_factor=backoff_factor)

        if not json_data:
            return None  # Exit if no valid data is retrieved

        items = json_data.get("items", [])
        if not items:
            return None  # Exit if no items are found

        # Create a dictionary with id as key and the item as the value
        for item in items:
            item_id = item.get("id")
            # if item_id:
                # all_data[item_id] = item  # Add item to dictionary with id as key
            if item_id:
                # Extract only necessary data using expected keys
                product_data[item_id] = {
                    key: item.get(key, default) for key, default in EXPECTED_PRODUCT_KEYS.items()
                }

        if offset + item_limit >= json_data.get("totalResults", 0):
            return product_data  # Return the dictionary of products once all data is fetched

        offset += item_limit


def stock_api_request(session: tls_client.Session, stock_url: str, product_data, item_limit: int,
                      offset: int = 0, max_retries: int = 3, delay: int = 5, backoff_factor: int = 2):
    """Fetch and validate product data with retry logic and return a dictionary with all expected attributes,
    but flattening 'productSkuInventoryStatus' into 'id' and 'totalStock'."""

    stock_data = {}
    product_ids = list(product_data.keys())

    while True:
        batch_ids = product_ids[offset:offset + item_limit]
        stock_url_current = f"{stock_url}?productIds=" + ",".join(batch_ids)
        json_data = _fetch_json(session, stock_url_current, retries=0, max_retries=max_retries, delay=delay,
                                backoff_factor=backoff_factor)

        if not json_data or "items" not in json_data:
            return None

        items = json_data["items"]

        if not items:
            return None

        for i, item in enumerate(items):
            if not item:
                logging.debug(f"Skipping empty item: {batch_ids[i]} in stock data response.")
                continue

            # Extract 'id' and 'totalStock' from 'productSkuInventoryStatus'
            inventory_status = item.get("productSkuInventoryStatus", {})
            if inventory_status:
                item_id, total_stock = next(iter(inventory_status.items()))

                # Preserve all expected stock attributes while flattening 'productSkuInventoryStatus'
                stock_data[item_id] = {
                    "id": item_id,
                    "totalStock": total_stock,
                    **{
                        key: item.get(
                            key,
                            item.get("productSkuInventoryDetails", [{}])[0].get(key,
                            item.get("productSkuInventoryStatus", {}).get(key, default))
                        )
                        for key, default in EXPECTED_STOCK_KEYS.items()
                    }
                }

        if offset + item_limit >= len(product_ids):
            return stock_data

        offset += item_limit



def process_products_with_or_without_stock_data(product_data, stock_data):
    """Process products and match them with stock data if available."""

    for product in product_data:
        try:
            # Look up the matching stock item using the product's id
            stock_item = stock_data.get(product)

            if stock_item:
                # Update the product with stock details if available
                product_data[product].update(stock_item)

        except Exception as e:
            logging.error(f"Error processing product {product}: {e}")

    # Store the products in the database
    try:
        store_products_to_db(product_data)
    except Exception as e:
        logging.error(f"Error storing products in the database: {e}")

def main():
    """Main function to fetch and process product data from the API."""
    start_time = time.time()
    initialize_logging()
    initialize_db()

    # Create session and handle API request
    session = create_session()

    product_data = product_api_request(session, PRODUCT_URL, CATEGORY_ID, ITEM_QUERY_LIMIT)

    # Fetch stock data for all products
    stock_data = stock_api_request(session, STOCK_URL, product_data, ITEM_QUERY_LIMIT)

    # Process products and store them to the database with or without stock data
    process_products_with_or_without_stock_data(product_data, stock_data)

    # End time tracking and print the execution time
    elapsed_time = time.time() - start_time
    logging.info(f"Execution completed in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    main()
