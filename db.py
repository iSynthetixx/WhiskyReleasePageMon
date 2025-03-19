import sqlite3
import logging
import os
from dotenv import load_dotenv

load_dotenv()  # Load the .env file
base_url = os.getenv("BASE_URL", "https://www.google.com")


def initialize_db():
    """Initializes the SQLite database and creates the necessary table if it doesn't exist."""
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


def has_product_changed(product):
    """Checks if the product values have changed by comparing with the database."""
    with sqlite3.connect('products.db') as conn:
        cursor = conn.cursor()

        # Use id to find the product in the database
        cursor.execute("SELECT * FROM products WHERE id = ?", (product.id,))
        existing_product = cursor.fetchone()

        if existing_product:
            existing_data = {
                "id": existing_product[0],
                "brand": existing_product[1],
                "displayName": existing_product[2],
                "inStockQuantity": existing_product[3],
                "orderableQuantity": existing_product[4],
                "listPrice": existing_product[5],
                "b2c_proof": existing_product[6],
                "b2c_size": existing_product[7],
                "stockStatus": existing_product[8],
                "lastModifiedDate": existing_product[9],
                "shippable": existing_product[10],
                "active": existing_product[11],
                "b2c_upc": existing_product[12],
                "primaryFullImageURL": existing_product[13],
            }

            list_of_changes = []
            for key, value in existing_data.items():
                # Default to None if the attribute does not exist
                product_value = getattr(product, key, None)
                # Compare the values
                if value != product_value:
                    logging.info(f"Product attribute: {key} for {product.displayName} has been updated.")
                    logging.info(f"Previous: {value}, Current: {product_value}.")
                    list_of_changes.append(f"Attribute {key} changed: {value} -> {product_value}")

            if list_of_changes:
                # Print the changes if any
                logging.info(f"Changes detected in product {product.displayName}:")
                for change in list_of_changes:
                    logging.info(change)
                # Product has changed
                return True

        else:
            # Product is new
            return True

    # No changes
    return False


def update_or_insert_product(product):
    """Updates an existing product or inserts a new one into the database."""
    with sqlite3.connect('products.db') as conn:
        cursor = conn.cursor()

        # Prepend the base URL to the primary image URL if it's not already prepended
        if product.primaryFullImageURL and not product.primaryFullImageURL.startswith(base_url):
            product.primaryFullImageURL = base_url + product.primaryFullImageURL

        # Set default values if attributes are not available
        product.brand = getattr(product, 'brand', "Unknown Brand")
        product.displayName = getattr(product, 'displayName', "Unknown Product")
        product.inStockQuantity = getattr(product, 'inStockQuantity', 0)
        product.orderableQuantity = getattr(product, 'orderableQuantity', 0)
        product.listPrice = getattr(product, 'listPrice', 0.0)
        product.b2c_proof = getattr(product, 'b2c_proof', "Unknown")
        product.b2c_size = getattr(product, 'b2c_size', "Unknown")
        product.stockStatus = getattr(product, 'stockStatus', "Unknown")
        product.lastModifiedDate = getattr(product, 'lastModifiedDate', "Unknown")
        product.shippable = getattr(product, 'shippable', False)
        product.active = getattr(product, 'active', True)
        product.b2c_upc = getattr(product, 'b2c_upc', "Unknown")

        # Use id as the key to check if the product already exists
        if has_product_changed(product):
            cursor.execute("""
            INSERT OR REPLACE INTO products (
                id, brand, displayName, inStockQuantity, orderableQuantity, listPrice, 
                b2c_proof, b2c_size, stockStatus, lastModifiedDate, 
                shippable, active, b2c_upc, primaryFullImageURL
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product.id,
                product.brand,
                product.displayName,
                product.inStockQuantity,
                product.orderableQuantity,
                product.listPrice,
                product.b2c_proof,
                product.b2c_size,
                product.stockStatus,
                product.lastModifiedDate,
                product.shippable,
                product.active,
                product.b2c_upc,
                product.primaryFullImageURL
            ))

            conn.commit()
            logging.info(f"Product: {product.displayName} has been inserted/updated in the database.")
        else:
            logging.info(f"Product: {product.displayName} has not changed, no update required.")


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
