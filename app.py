
import os
import sqlite3
import psutil

from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

from modules import (
    cpu_scheduling,
    memory_management,
    bankers_algorithm,
    disk_scheduling
)

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "OS_NEXUS_SECRET",
    "os-nexus-change-this-secret-key"
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

DB_PATH = "os_nexus.db"


# ---------------- DATABASE ----------------

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
init_db()


# ---------------- AUTHENTICATION ----------------

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:

            if request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "message": "Please login first"
                }), 401

            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return wrapper


# ---------------- HOME ----------------

@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Please fill all fields", "error")

        elif len(password) < 8:
            flash("Password must contain at least 8 characters", "error")

        elif password != confirm:
            flash("Passwords do not match", "error")

        else:

            try:
                password_hash = generate_password_hash(
                    password,
                    method="pbkdf2:sha256",
                    salt_length=16
                )

                with get_db() as db:
                    db.execute("""
                        INSERT INTO users(name, email, password_hash)
                        VALUES (?, ?, ?)
                    """, (name, email, password_hash))

                flash("Registration successful! Please login.", "success")
                return redirect(url_for("login"))

            except sqlite3.IntegrityError:
                flash("Email already registered", "error")

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        with get_db() as db:
            user = db.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()

        if user and check_password_hash(
            user["password_hash"], password
        ):

            session.clear()

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]

            return redirect(url_for("dashboard"))

        flash("Invalid email or password", "error")

    return render_template("login.html")


# ---------------- PROFILE ----------------

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    with get_db() as db:

        user = db.execute(
            "SELECT * FROM users WHERE id = ?",
            (session["user_id"],)
        ).fetchone()

        if not user:
            session.clear()
            return redirect(url_for("login"))

        if request.method == "POST":

            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not name or not email:
                flash("Name and email are required.", "error")

            elif "@" not in email or "." not in email.split("@")[-1]:
                flash("Please enter a valid email address.", "error")

            else:

                existing = db.execute(
                    "SELECT id FROM users WHERE email = ? AND id != ?",
                    (email, session["user_id"])
                ).fetchone()

                if existing:
                    flash("This email is already registered.", "error")

                elif new_password and not check_password_hash(
                    user["password_hash"], current_password
                ):
                    flash("Current password is incorrect.", "error")

                elif new_password and len(new_password) < 8:
                    flash("New password must contain at least 8 characters.", "error")

                elif new_password and new_password != confirm_password:
                    flash("New passwords do not match.", "error")

                else:

                    if new_password:

                        password_hash = generate_password_hash(
                            new_password,
                            method="pbkdf2:sha256",
                            salt_length=16
                        )

                        db.execute("""
                            UPDATE users
                            SET name = ?, email = ?, password_hash = ?
                            WHERE id = ?
                        """, (
                            name,
                            email,
                            password_hash,
                            session["user_id"]
                        ))

                    else:

                        db.execute("""
                            UPDATE users
                            SET name = ?, email = ?
                            WHERE id = ?
                        """, (
                            name,
                            email,
                            session["user_id"]
                        ))

                    db.commit()

                    session["user_name"] = name
                    session["user_email"] = email

                    flash("Profile updated successfully!", "success")
                    return redirect(url_for("profile"))

    return render_template("profile.html", user=user)


# ---------------- LOGOUT ----------------

@app.route("/logout", methods=["POST"])
@login_required
def logout():

    session.clear()

    flash("Logged out successfully", "success")

    return redirect(url_for("login"))


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "index.html",
        user_name=session.get("user_name"),
        user_email=session.get("user_email")
    )


# ---------------- SYSTEM MONITORING ----------------

@app.route("/api/health")
@login_required
def health():

    return jsonify({
        "success": True,
        "data": {"status": "online"}
    })


@app.route("/api/system")
@login_required
def system_stats():

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    data = {
        "cpu_percent": psutil.cpu_percent(interval=0.2),
        "memory_percent": memory.percent,
        "memory_used": memory.used,
        "memory_total": memory.total,
        "disk_percent": disk.percent,
        "disk_used": disk.used,
        "disk_total": disk.total
    }

    return jsonify({
        "success": True,
        "data": data
    })


# ---------------- CPU SCHEDULING ----------------

@app.route("/api/cpu", methods=["POST"])
@login_required
def cpu_api():

    try:
        data = request.get_json(force=True)
        result = cpu_scheduling(data)

        return jsonify({
            "success": True,
            "data": result
        })

    except (ValueError, KeyError, TypeError) as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 400


# ---------------- MEMORY MANAGEMENT ----------------

@app.route("/api/memory", methods=["POST"])
@login_required
def memory_api():

    try:
        data = request.get_json(force=True)
        result = memory_management(data)

        return jsonify({
            "success": True,
            "data": result
        })

    except (ValueError, KeyError, TypeError) as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 400


# ---------------- BANKER'S ALGORITHM ----------------

@app.route("/api/deadlock", methods=["POST"])
@login_required
def deadlock_api():

    try:
        data = request.get_json(force=True)
        result = bankers_algorithm(data)

        return jsonify({
            "success": True,
            "data": result
        })

    except (ValueError, KeyError, TypeError) as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 400


# ---------------- DISK SCHEDULING ----------------

@app.route("/api/disk", methods=["POST"])
@login_required
def disk_api():

    try:
        data = request.get_json(force=True)
        result = disk_scheduling(data)

        return jsonify({
            "success": True,
            "data": result
        })

    except (ValueError, KeyError, TypeError) as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 400


# ---------------- APPLICATION START ----------------

if __name__ == "__main__":


    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )
