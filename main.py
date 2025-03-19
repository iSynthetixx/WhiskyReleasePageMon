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

    if not proxy_file_path:
        logging.warning("PROXY_FILE environment variable is not set. Running without a proxy.")
        return session

    proxies = handle_proxies(proxy_file_path)

    if proxies:
        session.proxies.update({"http": proxies[0], "https": proxies[0]})
        logging.info(f"Using proxy: {proxies[0]}")
    else:
        logging.warning("No valid proxies found. Running without a proxy.")

    return session


def api_request(session: tls_client.Session, url, max_retries=3, delay=5, backoff_factor=2):
    """Fetches API data with retry logic for handling slow responses and specific HTTP status codes."""
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
            elif resp.status_code == 503:  # Service Unavailable
                logging.warning(f"Service unavailable (503). Retrying in {delay} seconds...")
                time.sleep(delay)
            elif resp.status_code == 403:  # Forbidden
                logging.error(f"Access forbidden (403). Check your proxy settings or permissions.")
                break
            else:
                logging.error(f"Received non-success status code {resp.status_code}. Retrying...")

        except requests.exceptions.Timeout:
            logging.error(f"Timeout error while accessing {url}. Retrying in {delay} seconds...")
            time.sleep(delay)
        except requests.exceptions.ConnectionError:
            logging.error(f"Connection error while accessing {url}. Retrying in {delay} seconds...")
            time.sleep(delay)
        except Exception as e:
            logging.error(f"Unexpected error while accessing {url}: {e}")
            if attempt < max_retries - 1:
                logging.warning(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds...")
                time.sleep(delay * backoff_factor)

    logging.error("Max retries reached. Exiting.")
    return None


def fetch_stock_data(session, product_data, stock_url):
    """Fetches stock data for products based on product IDs in the product data."""
    """product data is a json response from the api."""

    # Fetch stock data for products
    product_ids = [item["id"] for item in product_data.get("items", [])]

    if not product_ids:
        logging.error("No valid Product IDs found in 'items'. Stock levels will be unavailable.")
        return None  # Return None if no product IDs are available

    logging.debug(f"Successfully parsed {len(product_ids)} Product IDs.")
    stock_url_current = f"{stock_url},{','.join(product_ids)}"
    stock_data = api_request(session, stock_url_current)

    # Handle missing or malformed stock data
    if stock_data is None:
        logging.error("Failed to retrieve stock data!")
        return None
    elif not isinstance(stock_data.get("items"), list):
        logging.error("No 'items' found in the stock data response or invalid format.")
        return None

    logging.debug("Stock data successfully retrieved.")
    return stock_data

def process_products_with_or_without_stock_data(product_list, stock_data):
    """Process products and match them with stock data if available."""
    if stock_data:
        # Continue processing stock data
        for new_product in product_list:
            try:
                # Match each product with stock data
                for stock_item in stock_data.get("items", []):
                    if new_product.id in stock_item:
                        if "productSkuInventoryDetails" in stock_item and stock_item["productSkuInventoryDetails"]:
                            new_product.__dict__.update(stock_item["productSkuInventoryDetails"][0])
                        else:
                            logging.warning(f"No inventory details found for product ID: {new_product.id}")
                        break
            except ValidationError as e:
                logging.error(f"Error parsing stock levels: {e}")
                continue

    else:
        logging.warning("Stock data is unavailable, proceeding with available product data only.")

    # Store the products in the database
    try:
        store_products_to_db(product_list)
    except Exception as e:
        logging.error(f"Error storing products in the database: {e}")


def main():
    """Main function to fetch and process product data from the API."""
    start_time = time.time()
    initialize_logging()
    initialize_db()
    session = create_session()
    product_list = []
    product_data = api_request(session, product_url)

    # Ensure "items" key exists in the response and is a list type and is not empty or None
    if "items" not in product_data or not isinstance(product_data["items"], list) or not product_data["items"]:
        logging.warning("No 'items' found in the product data response or invalid format.")
        return

    # Create the new_product objects first before fetching stock data
    for item in product_data["items"]:
        try:
            # Validate and transform the product data using ItemModel
            new_product = ItemModel.model_validate(item)
            product_list.append(new_product)  # Store the product for later use with stock data
        except ValidationError as e:
            logging.error(f"Error parsing item: {e}")
            continue

    # Fetch stock data for products using the refactored function
    stock_data = fetch_stock_data(session, product_data, stock_url)

    # Process products with or without stock data
    process_products_with_or_without_stock_data(product_list, stock_data)

    # End time tracking and print the execution time
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f"Execution completed in {elapsed_time:.2f} seconds.")




if __name__ == "__main__":
    main()
