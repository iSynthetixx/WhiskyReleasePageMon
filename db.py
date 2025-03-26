import sqlite3
import logging
from dotenv import load_dotenv
from telegram_utils import *
import os

# Load environment variables from .env file
load_dotenv()  # Load the .env file
base_url = os.getenv("BASE_URL", "https://www.google.com")

# Combined dictionary with all expected product and stock attributes
PRODUCT_ATTRIBUTES = {
    "id": None, "brand": None, "active": None, "displayName": None,
    "primaryFullImageURL": None, "b2c_highlyAllocatedProduct": None,
    "x_volume": None, "listPrice": None,
    "onlineOnly": None, "creationDate": None, "b2c_onlineAvailable": None,
    "b2c_onlineExclusive": None, "lastModifiedDate": None, "b2c_size": None,
    "b2c_proof": None, "b2c_futuresProduct": None, "b2c_comingSoon": None,
    "repositoryId": None, "b2c_type": None,
    # Stock attributes
    "preOrderableQuantity": None,
    "orderableQuantity": None, "stockStatus": None, "availabilityDate": None, "backOrderableQuantity": None,
    "inStockQuantity": None,
    "totalStock": None,
    "url": None,
    "b2c_limitPerOrder": None
}


def initialize_db():
    """Ensures the products database table exists and creates it if missing."""
    try:
        with sqlite3.connect('products.db') as conn:
            cursor = conn.cursor()

            # Create table if it doesn't exist
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                brand TEXT,
                active TEXT,
                displayName TEXT,
                primaryFullImageURL TEXT,
                b2c_highlyAllocatedProduct TEXT,
                x_volume TEXT,
                listPrice TEXT,
                onlineOnly TEXT,
                creationDate TEXT,
                b2c_onlineAvailable TEXT,
                b2c_onlineExclusive TEXT,
                lastModifiedDate TEXT,
                b2c_size TEXT,
                b2c_proof TEXT,
                b2c_futuresProduct TEXT,
                b2c_comingSoon TEXT,
                repositoryId TEXT,
                b2c_type TEXT,
                preOrderableQuantity TEXT,
                orderableQuantity TEXT,
                stockStatus TEXT,
                availabilityDate TEXT,
                backOrderableQuantity TEXT,
                inStockQuantity TEXT,
                totalStock TEXT,
                url TEXT,
                b2c_limitPerOrder TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()
            logging.info("Database initialized successfully.")

    except sqlite3.Error as e:
        logging.error(f"Error initializing database: {e}")


def has_product_changed(product):
    """Checks if the product is new, unchanged, or changed in the database."""
    with sqlite3.connect('products.db') as conn:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM products WHERE id = ?
        """, (product['id'],))

        existing_product = cursor.fetchone()

        if existing_product is None:
            return "new"

        # Convert tuple to dictionary for comparison
        existing_data = dict(zip(PRODUCT_ATTRIBUTES.keys(), existing_product))

        for key, value in existing_data.items():
            # Ensure string comparison
            db_value = str(value) if value is not None else ""
            # Default to empty string
            api_value = str(product.get(key, ""))
            if db_value != api_value:
                logging.info(f"Product {product['displayName']} attribute {key} has changed "
                             f"from {db_value} to {api_value}.")
                return "changed"

        return "no_change"


def update_or_insert_product(product):
    """Inserts a new product or updates an existing one in the database if changes are detected."""
    try:
        with sqlite3.connect('products.db') as conn:
            cursor = conn.cursor()

            # Ensure the following remains a string
            product['active'] = str(product.get('active', ""))
            product['onlineOnly'] = str(product.get('onlineOnly', ""))
            product['availabilityDate'] = str(product.get('availabilityDate', ""))
            product['b2c_limitPerOrder'] = str(product.get('b2c_limitPerOrder', ""))

            # Prepends the base URL to the image link to fix it
            if product.get('primaryFullImageURL') and not product['primaryFullImageURL'].startswith(base_url):
                product['primaryFullImageURL'] = base_url + product['primaryFullImageURL']

            # Generates a link to the individual product as a new attribute URL
            product['url'] = base_url + "/product/" + product['id']

            product_status = has_product_changed(product)

            # Check the product status and insert or update the product accordingly
            if product_status == "new":
                cursor.execute(f"""
                INSERT INTO products (
                    {', '.join(PRODUCT_ATTRIBUTES.keys())},
                    last_updated, url
                ) VALUES ({', '.join('?' for _ in PRODUCT_ATTRIBUTES)}, CURRENT_TIMESTAMP, ?)
                """, (*[product.get(key) for key in PRODUCT_ATTRIBUTES], product['url']))
                conn.commit()
                logging.info(f"New product added: {product['displayName']}")

            elif product_status == "changed":
                cursor.execute(f"""
                UPDATE products SET
                    {', '.join([f"{key} = ?" for key in PRODUCT_ATTRIBUTES])},
                    last_updated = CURRENT_TIMESTAMP, url = ?
                WHERE id = ?
                """, (*[product.get(key) for key in PRODUCT_ATTRIBUTES], product['url'], product['id']))
                conn.commit()
                logging.info(f"Updated product: {product['displayName']}")

            else:
                logging.info(f"No changes detected for product: {product['displayName']}. Skipping update.")

    except sqlite3.Error as e:
        logging.error(f"Database error while updating product {product['displayName']}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in update_or_insert_product: {e}")


def store_products_to_db(product_list):
    """Stores the products in the list (a dictionary of dictionaries) to the database."""
    for product_id, product in product_list.items():
        try:
            # Ensure that each 'product' is a dictionary
            if not isinstance(product, dict):
                raise ValueError(f"Expected a dictionary for product {product_id}, but got {type(product)}")

            # Call the function to update or insert the product
            update_or_insert_product(product)
        except Exception as e:
            logging.error(f"Error storing product {product_id} ({product.get('displayName', 'Unknown product')}) to the database: {e}")


def delete_product(product_id):
    """Deletes a product from the database based on its ID."""
    with sqlite3.connect('products.db') as conn:
        cursor = conn.cursor()

        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        if cursor.rowcount > 0:
            logging.warning(f"Product: {product_id} deleted from the database.")
        else:
            logging.warning(f"Product: {product_id} not found in the database.")

        conn.commit()


def fetch_and_print_products():
    """Fetches and prints all products from the database."""
    with sqlite3.connect('products.db') as conn:
        cursor = conn.cursor()

        try:
            # Fetch all products from the database
            cursor.execute("SELECT * FROM products")
            rows = cursor.fetchall()

            # Iterate over each row and print the product details
            for row in rows:
                print(f"ID: {row[0]}")
                for i, key in enumerate(PRODUCT_ATTRIBUTES.keys()):
                    print(f"{key.capitalize()}: {row[i+1]}")  # Adjust index for the dynamic columns
                print("-" * 50)  # Separator for better readability

        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
