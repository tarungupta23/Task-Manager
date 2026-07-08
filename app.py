from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from mysql.connector import errorcode
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "replace-this-with-a-random-secret-key"  # change before deploying

# ---------------------------------------------------------------------------
# MySQL connection settings
# Replace "password" below with your own MySQL root/user password before
# launching the app, as requested.
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",   # <-- put your MySQL password here
    "database": "taskmanager",
}


def get_db_connection():
    """Return a fresh MySQL connection using mysql-connector-python."""
    return mysql.connector.connect(**DB_CONFIG)


# Predefined list of tasks shown in the "Task" dropdown
TASK_OPTIONS = [
    "Design",
    "Development",
    "Testing",
    "Documentation",
    "Deployment",
    "Bug Fixing",
    "Code Review",
    "Client Meeting",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped


# ---------------------------------------------------------------------------
# Auth pages
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password or not confirm_password:
            return render_template("register.html", error="All fields are required.")

        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match.")

        if len(password) < 6:
            return render_template("register.html", error="Password must be at least 6 characters long.")

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM users WHERE username = %s OR email = %s",
                (username, email),
            )
            if cursor.fetchone():
                return render_template("register.html", error="That username or email is already registered.")

            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password),
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

        return render_template(
            "login.html",
            success="Account created. You can now sign in.",
        )

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not email or not password:
            return render_template("login.html", error="Username, email and password are all required.")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM users WHERE username = %s AND email = %s",
                (username, email),
            )
            user = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if not user or not check_password_hash(user["password"], password):
            return render_template("login.html", error="Invalid username, email or password.")

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        username=session.get("username"),
        task_options=TASK_OPTIONS,
    )


# ---------------------------------------------------------------------------
# JSON API used by the frontend JavaScript
# ---------------------------------------------------------------------------
@app.route("/api/tasks", methods=["GET"])
@login_required
def api_get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return jsonify(rows)


@app.route("/api/tasks", methods=["POST"])
@login_required
def api_add_task():
    data = request.get_json(silent=True) or {}
    emp_id = (data.get("emp_id") or "").strip()
    emp_name = (data.get("emp_name") or "").strip()
    task_name = (data.get("task_name") or "").strip()
    completed = data.get("completed")

    if not all([emp_id, emp_name, task_name, completed]):
        return jsonify({"error": "All fields are required."}), 400
    if task_name not in TASK_OPTIONS:
        return jsonify({"error": "Invalid task selected."}), 400
    if completed not in ("Yes", "No"):
        return jsonify({"error": "Completed must be Yes or No."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO tasks (emp_id, emp_name, task_name, completed) VALUES (%s, %s, %s, %s)",
            (emp_id, emp_name, task_name, completed),
        )
        conn.commit()
        new_id = cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "id": new_id,
        "emp_id": emp_id,
        "emp_name": emp_name,
        "task_name": task_name,
        "completed": completed,
    }), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
@login_required
def api_update_task(task_id):
    data = request.get_json(silent=True) or {}
    emp_id = (data.get("emp_id") or "").strip()
    emp_name = (data.get("emp_name") or "").strip()
    task_name = (data.get("task_name") or "").strip()
    completed = data.get("completed")

    if not all([emp_id, emp_name, task_name, completed]):
        return jsonify({"error": "All fields are required."}), 400
    if task_name not in TASK_OPTIONS:
        return jsonify({"error": "Invalid task selected."}), 400
    if completed not in ("Yes", "No"):
        return jsonify({"error": "Completed must be Yes or No."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE tasks SET emp_id=%s, emp_name=%s, task_name=%s, completed=%s WHERE id=%s",
            (emp_id, emp_name, task_name, completed, task_id),
        )
        conn.commit()
        affected = cursor.rowcount
    finally:
        cursor.close()
        conn.close()

    if affected == 0:
        return jsonify({"error": "Task not found."}), 404
    return jsonify({"success": True})


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def api_delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
        conn.commit()
        affected = cursor.rowcount
    finally:
        cursor.close()
        conn.close()

    if affected == 0:
        return jsonify({"error": "Task not found."}), 404
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True)
