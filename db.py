import sqlite3
import logging


# Function to initialize the database
def initialize_db():
    """Initializes the SQLite database and creates the necessary table if it doesn't exist."""
    conn = sqlite3.connect('products.db')
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
    conn.close()


# Function to check if product has changed
def has_product_changed(product):
    """Checks if the product values have changed by comparing with the database."""
    conn = sqlite3.connect('products.db')
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

        changes = []  # List to keep track of changes
        for key, value in existing_data.items():
            product_value = getattr(product, key)  # Default to None if the attribute does not exist
            if value != product_value:  # Compare the values
                logging.info(f"{key} changed: Current in DB: {value} -> New in Product: {product_value}")

        if changes:
            # Print the changes if any
            logging.info(f"Changes detected in product {product.displayName}:")
            for change in changes:
                logging.info(change)

            conn.close()
            return True  # Product has changed
    else:
        conn.close()
        return True  # Product is new

    conn.close()
    return False  # No changes


# Function to update or insert a product into the database
def update_or_insert_product(product):
    """Updates an existing product or inserts a new one into the database."""
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    # Prepend the base URL to the primary image URL if it's not already prepended
    base_url = "https://www.finewineandgoodspirits.com"
    if product.primaryFullImageURL and not product.primaryFullImageURL.startswith(base_url):
        product.primaryFullImageURL = base_url + product.primaryFullImageURL

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

    conn.close()


# Function to store a list of products in the database
def store_products_to_db(product_list):
    """Stores the products in the list to the database."""
    for product in product_list:
        try:
            update_or_insert_product(product)
        except Exception as e:
            logging.error(f"Error storing product {product.displayName} to the database: {e}")


# Function to delete a product from the database
def delete_product(product_id):
    """Deletes a product from the database based on its ID."""
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    if cursor.rowcount > 0:
        logging.warning(f"Product: {product_id} deleted from the database.")
    else:
        logging.warning(f"Product: {product_id} not found in the database.")

    conn.commit()
    conn.close()


def fetch_and_print_products():
    """Fetches and prints all products from the database."""
    conn = sqlite3.connect('products.db')
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

    finally:
        conn.close()
