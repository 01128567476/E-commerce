import hashlib
import os
import sqlite3
import datetime
from flask import Flask, flash, redirect, render_template, request, session, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "db.sqlite3")
SECURITY_LOG = os.path.join(BASE_DIR, "security.log")

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "replace-this-with-a-secure-key")


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def log_security_event(message: str) -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SECURITY_LOG, "a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp} - {message}\n")


def hash_password(password: str) -> str:
    salt = "mini-store-salt"
    return hashlib.sha256(f"{password}{salt}".encode("utf-8")).hexdigest()


from init_db import init_db


def get_logged_user():
    return session.get("user")


@app.context_processor
def inject_cart_count():
    cart = session.get("cart", {})
    return {"cart_count": sum(item["quantity"] for item in cart.values())}


@app.route("/")
def index():
    user = get_logged_user()
    if user:
        return redirect(url_for("products"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not username or not email or not password or not confirm:
            flash("Please fill in all fields.", "warning")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Password and confirmation do not match.", "danger")
            return redirect(url_for("register"))

        hashed_password = hash_password(password)
        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, hashed_password, email),
            )
            conn.commit()
            conn.close()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists. Please choose another.", "danger")
            return redirect(url_for("register"))

    return render_template("register.html", user=get_logged_user())


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter your username and password.", "warning")
            return redirect(url_for("login"))

        hashed_password = hash_password(password)
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, hashed_password),
        ).fetchone()
        conn.close()

        if user:
            session["user"] = {"id": user["id"], "username": user["username"], "email": user["email"], "is_admin": user["is_admin"]}
            log_security_event(f"Successful login for {username}")
            flash(f"Welcome {user['username']}, you are now logged in.", "success")
            return redirect(url_for("products"))

        log_security_event(f"Failed login attempt for {username}")
        flash("Login credentials are incorrect.", "danger")
        return redirect(url_for("login"))

    if get_logged_user():
        return redirect(url_for("products"))

    return render_template("login.html", user=get_logged_user())


@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("cart", None)
    flash("تم تسجيل الخروج.", "info")
    return redirect(url_for("index"))


@app.route("/products")
def products():
    user = get_logged_user()
    if not user:
        flash("Please log in to continue shopping.", "warning")
        return redirect(url_for("login"))

    if user.get("is_admin"):
        return redirect(url_for("admin_products"))

    conn = get_db_connection()
    product_rows = conn.execute("SELECT * FROM products WHERE stock > 0 ORDER BY id").fetchall()
    conn.close()
    return render_template("products.html", products=product_rows, user=user)


@app.route("/admin/products", methods=["GET"])
def admin_products():
    user = get_logged_user()
    if not user or not user.get("is_admin"):
        flash("Access denied. Admin panel is restricted.", "danger")
        return redirect(url_for("products"))

    conn = get_db_connection()
    product_rows = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
    conn.close()
    return render_template("admin_products.html", products=product_rows, user=user)


@app.route("/admin/products/update-stock/<int:product_id>", methods=["POST"])
def update_stock(product_id):
    user = get_logged_user()
    if not user or not user.get("is_admin"):
        flash("Access denied. Admin panel is restricted.", "danger")
        return redirect(url_for("products"))

    amount = request.form.get("amount", "0").strip()
    if not amount.isdigit():
        flash("Please enter a valid stock amount.", "warning")
        return redirect(url_for("admin_products"))

    amount = int(amount)
    if amount <= 0:
        flash("Quantity must be greater than zero.", "warning")
        return redirect(url_for("admin_products"))

    conn = get_db_connection()
    conn.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (amount, product_id))
    conn.commit()
    conn.close()

    flash("Product stock updated successfully.", "success")
    return redirect(url_for("admin_products"))


@app.route("/product/<int:product_id>/add")
def add_to_cart(product_id):
    if not get_logged_user():
        flash("Please log in to add items to your cart.", "warning")
        return redirect(url_for("login"))

    user = get_logged_user()
    if user.get("is_admin"):
        flash("Admin users can manage stock from the admin panel.", "info")
        return redirect(url_for("admin_products"))

    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()

    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("products"))

    cart = session.get("cart", {})
    cart_item = cart.get(str(product_id), {"id": product_id, "name": product["name"], "price": product["price"], "quantity": 0})
    cart_item["quantity"] += 1
    cart[str(product_id)] = cart_item
    session["cart"] = cart

    flash(f"{product['name']} has been added to your cart.", "success")
    return redirect(url_for("products"))


@app.route("/cart")
def view_cart():
    user = get_logged_user()
    if not user:
        flash("Please log in to view your cart.", "warning")
        return redirect(url_for("login"))
    if user.get("is_admin"):
        flash("Admin users do not use the shopping cart.", "info")
        return redirect(url_for("admin_products"))

    cart = session.get("cart", {})
    total = sum(item["quantity"] * item["price"] for item in cart.values())
    return render_template("cart.html", cart=cart, total=total, user=user)


@app.route("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):
    user = get_logged_user()
    if not user:
        flash("Please log in to continue.", "warning")
        return redirect(url_for("login"))
    if user.get("is_admin"):
        flash("Admin users do not use the shopping cart.", "info")
        return redirect(url_for("admin_products"))

    cart = session.get("cart", {})
    if str(product_id) in cart:
        cart.pop(str(product_id))
        session["cart"] = cart
        flash("Product removed from cart.", "info")
    return redirect(url_for("view_cart"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    user = get_logged_user()
    if not user:
        flash("Please log in to complete checkout.", "warning")
        return redirect(url_for("login"))
    if user.get("is_admin"):
        flash("Admin users do not place orders.", "info")
        return redirect(url_for("admin_products"))

    cart = session.get("cart", {})
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("products"))

    total = sum(item["quantity"] * item["price"] for item in cart.values())
    if request.method == "POST":
        address = request.form.get("address", "").strip()
        email = request.form.get("email", "").strip()

        if not address or not email:
            flash("Please enter your email and shipping address.", "warning")
            return redirect(url_for("checkout"))

        conn = get_db_connection()
        
        # Check stock availability
        all_stock_ok = True
        for product_id, item in cart.items():
            product = conn.execute("SELECT stock FROM products WHERE id = ?", (int(product_id),)).fetchone()
            if not product or product["stock"] < item["quantity"]:
                flash(f"Insufficient stock for {item['name']}. Available: {product['stock'] if product else 0}", "danger")
                all_stock_ok = False
                break
        
        if not all_stock_ok:
            conn.close()
            return redirect(url_for("view_cart"))
        
        # Deduct stock for each product in the order
        for product_id, item in cart.items():
            conn.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (item["quantity"], int(product_id)),
            )

        order_items = [f"{item['quantity']}x {item['name']}" for item in cart.values()]
        items_text = ", ".join(order_items)

        conn.execute(
            "INSERT INTO orders (user_id, items, total, address, email, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
            (user["id"], items_text, total, address, email),
        )
        conn.commit()
        conn.close()

        session.pop("cart", None)
        flash("Order confirmed successfully.", "success")
        return render_template("order_success.html", total=total, user=user)

    return render_template("checkout.html", cart=cart, total=total, user=user)


@app.route("/orders")
def orders():
    user = get_logged_user()
    if not user:
        flash("Please log in to view your orders.", "warning")
        return redirect(url_for("login"))
    if user.get("is_admin"):
        flash("Admin users do not have personal orders.", "info")
        return redirect(url_for("admin_products"))

    conn = get_db_connection()
    order_rows = conn.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (user["id"],)).fetchall()
    conn.close()
    return render_template("orders.html", orders=order_rows, user=user)


@app.route("/admin/users")
def admin_users():
    user = get_logged_user()
    if not user or not user.get("is_admin"):
        flash("Access denied. Admin panel is restricted.", "danger")
        return redirect(url_for("products"))
    
    conn = get_db_connection()
    users = conn.execute("SELECT id, username, email, is_admin FROM users ORDER BY id").fetchall()
    conn.close()
    
    login_log = []
    if os.path.exists(SECURITY_LOG):
        with open(SECURITY_LOG, "r", encoding="utf-8") as log_file:
            login_log = log_file.readlines()[-50:]
    
    return render_template("admin_users.html", users=users, login_log=login_log, user=user)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
