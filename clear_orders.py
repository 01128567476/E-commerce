import sqlite3

conn = sqlite3.connect("db.sqlite3")

conn.execute("DELETE FROM orders")

conn.commit()
conn.close()

print("Orders deleted.")