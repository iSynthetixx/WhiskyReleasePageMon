import sqlite3
import logging
import os
from dotenv import load_dotenv
from telegram_utils import *

load_dotenv()  # Load the .env file
base_url = os.getenv("BASE_URL", "https://www.google.com")


def initialize_db():
    """Initializes the SQLite database and creates the necessary table if it doesn't exist."""
    try:
        with sqlite3.connect('products.db') as conn:
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                brand TEXT,
                displayName TEXT,
                inStockQuantity INTEGER,
                orderableQuantity INTEGER,
                listPrice REAL,
                b2c_proof TEXT,
                b2c_size TEXT,
                stockStatus TEXT,
                lastModifiedDate TEXT,
                shippable BOOLEAN,
                active BOOLEAN,
                b2c_upc TEXT,
                primaryFullImageURL TEXT,
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
        SELECT brand, displayName, inStockQuantity, orderableQuantity, listPrice, 
               b2c_proof, b2c_size, stockStatus, lastModifiedDate, 
               shippable, active, b2c_upc, primaryFullImageURL
        FROM products WHERE id = ?
        """, (product.id,))

        existing_product = cursor.fetchone()

        if existing_product is None:
            return "new"

        # Convert tuple to dictionary
        existing_data = dict(zip(
            ["brand", "displayName", "inStockQuantity", "orderableQuantity", "listPrice",
             "b2c_proof", "b2c_size", "stockStatus", "lastModifiedDate",
             "shippable", "active", "b2c_upc", "primaryFullImageURL"], existing_product
        ))

        for key, value in existing_data.items():
            if value != getattr(product, key, None):
                return "changed"

        return "no_change"


def update_or_insert_product(product):
    """Inserts a new product or updates an existing one in the database if changes are detected."""
    try:
        with sqlite3.connect('products.db') as conn:
            cursor = conn.cursor()

            if product.primaryFullImageURL and not product.primaryFullImageURL.startswith(base_url):
                product.primaryFullImageURL = base_url + product.primaryFullImageURL

            product_status = has_product_changed(product)

            if product_status == "new":
                cursor.execute("""
                INSERT INTO products (
                    id, brand, displayName, inStockQuantity, orderableQuantity, listPrice, 
                    b2c_proof, b2c_size, stockStatus, lastModifiedDate, 
                    shippable, active, b2c_upc, primaryFullImageURL
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product.id, product.brand, product.displayName, product.inStockQuantity,
                    product.orderableQuantity, product.listPrice, product.b2c_proof,
                    product.b2c_size, product.stockStatus, product.lastModifiedDate,
                    product.shippable, product.active, product.b2c_upc, product.primaryFullImageURL
                ))
                conn.commit()

                message = (
                    f"🆕 *New Product Added!*\n"
                    f"📌 *{product.displayName}*\n"
                    f"🏷️ Brand: {product.brand}\n"
                    f"📦 In Stock: {product.inStockQuantity}\n"
                    f"💰 Price: ${product.listPrice}\n"
                    f"🛒 Orderable Quantity: {product.orderableQuantity}\n"
                    f"🔗 [View Product]({product.primaryFullImageURL})"
                )

                send_telegram_message(message)
                logging.info(f"New product added: {product.displayName}")


            elif product_status == "changed":
                cursor.execute("""
                UPDATE products SET
                    brand = ?, displayName = ?, inStockQuantity = ?, orderableQuantity = ?, 
                    listPrice = ?, b2c_proof = ?, b2c_size = ?, stockStatus = ?, 
                    lastModifiedDate = ?, shippable = ?, active = ?, b2c_upc = ?, 
                    primaryFullImageURL = ? WHERE id = ?
                """, (
                    product.brand, product.displayName, product.inStockQuantity,
                    product.orderableQuantity, product.listPrice, product.b2c_proof,
                    product.b2c_size, product.stockStatus, product.lastModifiedDate,
                    product.shippable, product.active, product.b2c_upc,
                    product.primaryFullImageURL, product.id
                ))
                conn.commit()
                logging.info(f"Updated product: {product.displayName}")

            else:
                logging.info(f"No changes detected for product: {product.displayName}. Skipping update.")

    except sqlite3.Error as e:
        logging.error(f"Database error while updating product {product.displayName}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in update_or_insert_product: {e}")


def store_products_to_db(product_list):
    """Stores the products in the list to the database."""
    for product in product_list:
        try:
            update_or_insert_product(product)
        except Exception as e:
            logging.error(f"Error storing product {product.displayName} to the database: {e}")


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
                print(f"Brand: {row[1]}")
                print(f"Display Name: {row[2]}")
                print(f"In Stock Quantity: {row[3]}")
                print(f"Orderable Quantity: {row[4]}")
                print(f"List Price: {row[5]}")
                print(f"B2C Proof: {row[6]}")
                print(f"B2C Size: {row[7]}")
                print(f"Stock Status: {row[8]}")
                print(f"Last Modified Date: {row[9]}")
                print(f"Shippable: {row[10]}")
                print(f"Active: {row[11]}")
                print(f"B2C UPC: {row[12]}")
                print(f"Primary Image URL: {row[13]}")
                print("-" * 50)  # Separator for better readability

        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
