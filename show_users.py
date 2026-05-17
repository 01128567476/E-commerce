import sqlite3

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()
users = cursor.execute("SELECT * FROM users").fetchall()
print(users)
conn.close()