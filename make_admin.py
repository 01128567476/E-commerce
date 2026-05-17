#!/usr/bin/env python3
"""
Usage: python make_admin.py <username>
"""

import sqlite3
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "db.sqlite3")


def make_admin(username):
    if not os.path.exists(DATABASE_PATH):
        print("Error: Database not found. Run 'python init_db.py' first.")
        return False

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check if user exists
    user = cursor.execute("SELECT id, username FROM users WHERE username = ?", (username,)).fetchone()
    
    if not user:
        print(f"Error: User '{username}' not found.")
        conn.close()
        return False

    # Make user an admin
    cursor.execute("UPDATE users SET is_admin = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()

    print(f"✓ User '{username}' is now an admin.")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python make_admin.py <username>")
        print("Example: python make_admin.py ahmed")
        sys.exit(1)

    username = sys.argv[1]
    make_admin(username)
