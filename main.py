import tls_client
import os
from dotenv import load_dotenv
import logging
import colorlog
from logging.handlers import RotatingFileHandler
import time
from pydantic import ValidationError
from models import ItemModel
import requests
from db import *


# Load environment variables from .env file
load_dotenv()
# Access the environment variables
product_url = os.getenv("PRODUCT_URL")
stock_url = os.getenv("STOCK_URL")
log_file_path = os.getenv("LOG_FILE_PATH")
proxy_file_path = os.getenv("PROXY_FILE")


def initialize_logging():
    """Configures the logging setup to log to both console and file with rotation."""
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
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
        log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(log_formatter)
    logging.basicConfig(level=logging.INFO, handlers=[console_handler, file_handler])


# Proxy validation functions
def check_proxy(proxy):
    """Checks if the given proxy is working."""
    try:
        response = requests.get('https://httpbin.org/ip', proxies={"http": proxy, "https": proxy}, timeout=10)
        if response.status_code == 200:
            return True
        else:
            logging.warning(f"Proxy {proxy} failed with status code {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Error with proxy {proxy}: {e}")
    return False


def load_proxies_from_file(file_path):
    """Loads proxy addresses from a .txt file."""
    try:
        with open(file_path, 'r') as f:
            proxies = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        logging.error(f"Proxy file {file_path} not found.")
        return []
    return proxies


def save_proxies_to_file(file_path, proxies):
    """Saves the list of proxies back to the .txt file."""
    with open(file_path, 'w') as f:
        for proxy in proxies:
            f.write(f"{proxy}\n")


def validate_and_clean_proxies(proxy_file_path):
    """Validate proxies and remove dead ones from the proxy file."""
    proxies = load_proxies_from_file(proxy_file_path)
    valid_proxies = []

    for proxy in proxies:
        if check_proxy(proxy):
            valid_proxies.append(proxy)
        else:
            logging.warning(f"Removing dead proxy: {proxy}")

    save_proxies_to_file(proxy_file_path, valid_proxies)
    logging.info(f"Proxy file updated. {len(valid_proxies)} valid proxies remaining.")


def load_proxies_from_env():
    """Validate and load proxies from the environment-defined proxy file."""
    if not proxy_file_path:
        logging.error("PROXY_FILE environment variable is not set.")
        return []

    validate_and_clean_proxies(proxy_file_path)
    return load_proxies_from_file(proxy_file_path)


# Create a session with TLS client
def create_session():
    """Creates a session with TLS client and configures proxy."""
    session = tls_client.Session(client_identifier="chrome_120", random_tls_extension_order=True)

    # Get the proxies list from the cleaned proxies file
    proxies = load_proxies_from_env()

    if proxies:
        proxy = proxies[0]  # Use the first valid proxy
        session.proxies.update({"http": proxy, "https": proxy})
        logging.info(f"Using proxy: {proxy}")
    else:
        logging.warning("No valid proxies found. Running without a proxy.")

    return session


def api_request(session: tls_client.Session, url, max_retries=3, delay=5):
    """Fetches API data with retry logic for handling slow responses."""
    for attempt in range(max_retries):
        try:
            logging.debug(f"Fetching data from {url}... (Attempt {attempt + 1})")
            resp = session.get(url)
            # Check if the response status code is in the 2xx range (success)
            if 200 <= resp.status_code < 300:
                try:
                    return resp.json()  # Ensure response is valid JSON
                except ValueError:
                    logging.error(f"Failed to decode JSON response. Response Text: {resp.text}")
                    return None
            else:
                logging.error(f"Received non-success status code {resp.status_code}")

        except Exception as e:
            logging.error(f"Error fetching API data: {e}")
            if attempt < max_retries - 1:
                logging.warning(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds...")
                time.sleep(delay)

    logging.error("Max retries reached. Exiting.")
    return None


def main():
    """Main function to fetch and process product data from the API."""
    start_time = time.time()
    initialize_logging()
    initialize_db()
    product_list = []
    session = create_session()
    product_data = api_request(session, product_url)

    if not product_data:
        logging.error("Failed to retrieve data. Exiting...")
        return

    # Ensure "items" key exists in the response
    if "items" not in product_data or not isinstance(product_data["items"], list) or not product_data["items"]:
        logging.warning("No 'items' found in the product data response or invalid format.")
        return

    # Fetch stock data for products
    product_ids = [item["id"] for item in product_data["items"]]

    if product_ids:
        logging.debug("Successfully parsed Product ID's.")
        stock_url_current = stock_url + ",".join(product_ids)
        stock_data = api_request(session, stock_url_current)
        if not stock_data:
            logging.error("Failed to retrieve stock data!")
        if "items" not in stock_data or not isinstance(stock_data["items"], list):
            logging.error("No 'items' found in the stock data response or invalid format.")
    else:
        logging.error("No Product ID's parsed from 'items' or invalid format. Stock levels will be unavailable.")

    if not product_data["items"]:
        logging.warning("List of items from API returned empty.")
    else:
        # Process each item in the product data
        for item in product_data["items"]:
            try:
                # Validate and transform the product data using ItemModel
                new_product = ItemModel.model_validate(item)
                try:
                    for index, dictionary in enumerate(stock_data["items"]):
                        if new_product.id in dictionary:
                            if "productSkuInventoryDetails" in dictionary and dictionary["productSkuInventoryDetails"]:
                                new_product.__dict__.update(dictionary["productSkuInventoryDetails"][0])
                            else:
                                logging.warning(f"No inventory details found for product ID: {new_product.id}")
                            break
                except ValidationError as e:
                    logging.error(f"Error parsing stock levels: {e}")
                    continue
                # Append the validated product to the product list
                product_list.append(new_product)
            except ValidationError as e:
                logging.error(f"Error parsing item: {e}")
                continue

    # Store the products in the database
    store_products_to_db(product_list)

    # End time tracking and print the execution time
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f"Execution completed in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    main()
