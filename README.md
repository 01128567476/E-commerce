<<<<<<< HEAD
# Mini E-Commerce System

A professional mini e-commerce store with:
- User registration and login
- Product listing from a SQLite database
- Shopping cart and checkout flow
- Order storage with order history
- Basic security with password hashing and safe SQL queries

## Run the Project

1. Open the command prompt in the project folder:
   `cd "c:\Users\METRO\Desktop\New folder (3)"`
2. Create a virtual environment:
   `python -m venv venv`
3. Activate the environment:
   `venv\Scripts\activate`
4. Install requirements:
   `pip install -r requirements.txt`
5. Create the database and load sample products:
   `python init_db.py`
6. Run the application:
   `python app.py`
7. Open the browser at:
   `http://127.0.0.1:5000`

## Notes
- Set `FLASK_SECRET_KEY` in the environment for better session security.
- You can edit products in `init_db.py` or directly within the SQLite database.
- Product images live in `static/images/` and are referenced from the database.
- If you change `PRODUCT_DATA` after `db.sqlite3` exists, delete `db.sqlite3` and rerun `python init_db.py` to refresh the sample data.
=======
# E-commerce
>>>>>>> 2a3ede0222190451d583a322be632f92df838783
