import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "db.sqlite3")

PRODUCT_DATA = [
    ("Aurora Smart Phone", "Sleek performance phone with AI camera and long battery life.", 799.00, 26, "images/phone.svg"),
    ("Cloud Shield Case", "Slim hardshell case with shock protection and soft interior.", 29.00, 74, "images/phone_case.svg"),
    ("Magnetic Wireless Charger", "Fast wireless charging pad for seamless desk charging.", 39.00, 62, "images/wireless_car_charger.svg"),
    ("Clear Screen Protector", "Premium glass screen protector with anti-fingerprint coating.", 19.00, 88, "images/screen_protector.svg"),
    ("Ultra Comfort Earbuds", "True wireless earbuds with crisp sound and long battery life.", 89.00, 45, "images/earbuds.svg"),
    ("Travel Power Bank", "Slim power bank with dual USB ports and fast charge support.", 45.00, 53, "images/power_bank.svg"),
    ("Phone Grip Stand", "Adjustable stand with secure grip for easy hands-free use.", 24.00, 65, "images/foldable_phone_stand.svg"),
    ("Lightning Cable Pack", "Durable braided charging cable set with fast sync support.", 18.00, 98, "images/cable_pack.svg"),
    ("Noise Reduction Earbuds", "Compact buds with active noise reduction and rich audio.", 74.00, 39, "images/earbuds.svg"),
    ("Classic Power Adapter", "Compact fast charger with universal plug compatibility.", 22.00, 84, "images/power_adapter.svg"),
    ("Wireless Car Charger", "Smart car mount with fast charging and secure magnetic hold.", 49.00, 58, "images/wireless_car_charger.svg"),
    ("Foldable Phone Stand", "Portable stand with multiple viewing angles for desk and travel.", 27.00, 72, "images/foldable_phone_stand.svg"),
    ("MagSafe Wallet", "Magnetic wallet attachment for cards and cash with premium leather finish.", 34.00, 40, "images/magsafe_wallet.svg"),
    ("Gaming Phone Cooler", "Compact cooling fan to keep phones cool during long gaming sessions.", 56.00, 31, "images/gaming_phone_cooler.svg"),
]

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            image_url TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            items TEXT NOT NULL,
            total REAL NOT NULL,
            address TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    current_columns = [row[1] for row in cursor.execute("PRAGMA table_info(products)").fetchall()]
    if "image_url" not in current_columns:
        cursor.execute("ALTER TABLE products ADD COLUMN image_url TEXT")

    user_columns = [row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()]
    if "is_admin" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")

    current_products = cursor.execute("SELECT name, image_url FROM products ORDER BY id").fetchall()
    if len(current_products) != len(PRODUCT_DATA):
        refresh = True
    else:
        refresh = any(
            current_products[i][0] != expected[0] or current_products[i][1] != expected[4]
            for i, expected in enumerate(PRODUCT_DATA)
        )

    if refresh:
        cursor.execute("DELETE FROM products")
        cursor.executemany(
            "INSERT INTO products (name, description, price, stock, image_url) VALUES (?, ?, ?, ?, ?)",
            PRODUCT_DATA,
        )
        print("Updated products table with the latest catalog.")
    else:
        print("Database exists. Products table is ready.")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
