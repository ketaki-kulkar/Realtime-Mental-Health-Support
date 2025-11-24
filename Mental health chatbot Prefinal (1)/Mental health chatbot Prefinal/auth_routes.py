from flask import Blueprint, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)
main = Blueprint("main", __name__)

# Database connection
DB_HOST = 'localhost'  # Change to your MySQL host
DB_USER = 'root'       # Your MySQL username
DB_PASSWORD = ''  # Your MySQL password
DB_NAME = 'mental_health_chatbot'   # The database name

# Login route
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session["userId"] = user[0]  # Store user name in session
            session["userName"] = user[1]  # Store user name in session
            return redirect(url_for("main.home"))
        else:
            return render_template("login.html", error="Invalid email or password.")
    return render_template("login.html")

# Signup route
@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
            conn.commit()
            conn.close()
            
            return redirect(url_for("auth.login"))
        except mysql.connector.IntegrityError:
            return render_template("signup.html", error="Email already exists.")
    return render_template("signup.html")

# Logout route
@auth.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("auth.login"))
