from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey"

# ---------------- DATABASE SETUP ---------------- #

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clubs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            clubname TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template("index.html")

# -------- Register -------- #

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return "User already exists!"

        # Insert new user
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# -------- Login -------- #

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin")

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                       (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid credentials!"

    return render_template("login.html")

# -------- Dashboard -------- #

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    clubs = [
    "Singing Club",
    "Dancing Club",
    "Coding Club",
    "Creativity Club",
    "Business Club",
    "Donation Club",
    "Gaming Club"
]

    if request.method == "POST":
        selected_clubs = request.form.getlist("clubs")
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        for club in selected_clubs:
            cursor.execute("INSERT INTO clubs (username,clubname) VALUES (?,?)",
                           (session["user"], club))

        conn.commit()
        conn.close()

    return render_template("dashboard.html", clubs=clubs)

# -------- Admin -------- #

@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT clubname, COUNT(*) FROM clubs GROUP BY clubname")
    data = cursor.fetchall()

    conn.close()
    return render_template("admin.html", data=data)

# -------- Logout -------- #

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/admin_members")
def admin_members():
    if "admin" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, username, clubname FROM clubs")
    members = cursor.fetchall()
    conn.close()

    return render_template("admin_members.html", members=members)


# -------- Add Member -------- #

@app.route("/admin_add", methods=["POST"])
def admin_add():
    if "admin" not in session:
        return redirect("/login")

    username = request.form["username"]
    clubname = request.form["clubname"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clubs (username, clubname) VALUES (?,?)",
                   (username, clubname))
    conn.commit()
    conn.close()

    return redirect("/admin_members")


# -------- Delete Member -------- #

@app.route("/admin_delete/<int:id>")
def admin_delete(id):
    if "admin" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clubs WHERE rowid=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin_members")

if __name__ == "__main__":
    app.run(debug=True)