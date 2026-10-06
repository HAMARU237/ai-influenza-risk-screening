from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

# สำหรับใช้งานจริงควรเปลี่ยนเป็น Secret Key ของคุณเอง
app.secret_key = "change-this-secret-key"


# =========================================================
# USER DATABASE
# =========================================================

USER_FILE = "users.json"


def load_users():

    if not os.path.exists(USER_FILE):
        return {}

    try:

        with open(
            USER_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (json.JSONDecodeError, OSError):

        return {}


def save_users(users):

    with open(
        USER_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            users,
            file,
            ensure_ascii=False,
            indent=4
        )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        users = load_users()

        user = users.get(username)

        # ตรวจสอบ Username + Password
        if user and check_password_hash(
            user["password"],
            password
        ):

            session["logged_in"] = True

            session["username"] = username

            return redirect(
                url_for("home")
            )

        return render_template(
            "login.html",
            error="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"
        )

    return render_template(
        "login.html"
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )


        # ตรวจสอบ Username
        if len(username) < 4:

            return render_template(
                "register.html",
                error="ชื่อผู้ใช้ต้องมีอย่างน้อย 4 ตัวอักษร"
            )


        # ตรวจสอบ Password
        if len(password) < 6:

            return render_template(
                "register.html",
                error="รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร"
            )


        # ตรวจสอบ Password ซ้ำ
        if password != confirm_password:

            return render_template(
                "register.html",
                error="รหัสผ่านทั้งสองช่องไม่ตรงกัน"
            )


        users = load_users()


        # ตรวจสอบ Username ซ้ำ
        if username in users:

            return render_template(
                "register.html",
                error="ชื่อผู้ใช้นี้ถูกใช้งานแล้ว"
            )


        # สร้าง User
        users[username] = {

            "username": username,

            "password": generate_password_hash(
                password
            )

        }


        save_users(users)


        return redirect(
            url_for(
                "login",
                registered="1"
            )
        )


    return render_template(
        "register.html"
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    # ถ้ายังไม่ได้ Login
    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )


    return render_template(
        "index.html",
        username=session.get("username")
    )


# =========================================================
# INFLUENZA INFORMATION
# =========================================================

@app.route("/info")
def info():

    # ถ้ายังไม่ได้ Login
    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )


    return render_template(
        "info.html",
        username=session.get("username")
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# 404 ERROR
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <!DOCTYPE html>

    <html lang="th">

    <head>

        <meta charset="UTF-8">

        <title>404</title>

        <style>

            body {
                background: #080808;
                color: white;
                font-family: Arial, sans-serif;
                text-align: center;
                padding-top: 100px;
            }

            a {
                color: #ff3333;
            }

        </style>

    </head>

    <body>

        <h1>404 - Page Not Found</h1>

        <p>
            ไม่พบหน้าที่คุณกำลังเรียกใช้งาน
        </p>

        <a href="/">
            กลับหน้าหลัก
        </a>

    </body>

    </html>
    """, 404


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )