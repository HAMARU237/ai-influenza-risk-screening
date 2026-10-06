from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

import json
import os
import joblib
import pandas as pd


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

# สำหรับใช้งานจริงควรเปลี่ยนเป็น Secret Key ของคุณเอง
app.secret_key = "change-this-secret-key"


# =========================================================
# MACHINE LEARNING MODEL
# =========================================================

MODEL_FILE = "model.pkl"
FEATURE_FILE = "features.pkl"

model = None
features = []


def load_ml_model():

    global model
    global features

    try:

        if os.path.exists(MODEL_FILE):

            model = joblib.load(MODEL_FILE)

        if os.path.exists(FEATURE_FILE):

            features = joblib.load(FEATURE_FILE)

        print("========================================")
        print("Machine Learning Model")
        print("========================================")

        print("Model loaded:", model is not None)
        print("Features:", features)

    except Exception as error:

        print("Error loading ML model:")
        print(error)

        model = None
        features = []


# Load model when Flask starts
load_ml_model()


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
# HOME / AI SCREENING
# =========================================================

@app.route(
    "/",
    methods=["GET", "POST"]
)
def home():

    # ถ้ายังไม่ได้ Login
    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )


    # =====================================================
    # GET
    # =====================================================

    if request.method == "GET":

        return render_template(
            "index.html",
            username=session.get("username")
        )


    # =====================================================
    # POST - AI PREDICTION
    # =====================================================

    if model is None:

        return render_template(
            "index.html",
            username=session.get("username"),
            error="ไม่พบ Machine Learning Model กรุณาตรวจสอบ model.pkl"
        )


    try:

        # -------------------------------------------------
        # รับข้อมูลจาก HTML Form
        # -------------------------------------------------

        age = int(
            request.form.get(
                "age",
                0
            )
        )


        gender_text = request.form.get(
            "gender",
            "Male"
        )


        fever = int(
            request.form.get(
                "fever",
                0
            )
        )


        cough = int(
            request.form.get(
                "cough",
                0
            )
        )


        sore = int(
            request.form.get(
                "sore",
                0
            )
        )


        headache = int(
            request.form.get(
                "headache",
                0
            )
        )


        malaise = int(
            request.form.get(
                "malaise",
                0
            )
        )


        runny = int(
            request.form.get(
                "runny",
                0
            )
        )


        generalized = int(
            request.form.get(
                "generalized",
                0
            )
        )


        chill = int(
            request.form.get(
                "chill",
                0
            )
        )


        # -------------------------------------------------
        # Convert Gender
        # Dataset:
        # Male = 1
        # Female = 0
        # -------------------------------------------------

        if gender_text == "Male":

            gender = 1

        else:

            gender = 0


        # -------------------------------------------------
        # สร้างข้อมูลตามลำดับ Features ของ Model
        # -------------------------------------------------

        input_data = {

            "Age": age,

            "Gender": gender,

            "Sec3_Fever": fever,

            "Sec3_Cough": cough,

            "Sec3_Sore": sore,

            "Sec3_Headache": headache,

            "Sec3_Malaise": malaise,

            "Sec3_Runny": runny,

            "Sec3_Generalized": generalized,

            "Sec3_Chill": chill

        }


        # -------------------------------------------------
        # สร้าง DataFrame
        # -------------------------------------------------

        input_df = pd.DataFrame(
            [input_data]
        )


        # -------------------------------------------------
        # เรียง Features ให้ตรงกับตอน Training
        # -------------------------------------------------

        input_df = input_df[
            features
        ]


        # -------------------------------------------------
        # Prediction
        # -------------------------------------------------

        prediction = model.predict(
            input_df
        )[0]


        # -------------------------------------------------
        # Probability
        # -------------------------------------------------

        probability = None

        if hasattr(
            model,
            "predict_proba"
        ):

            probability = model.predict_proba(
                input_df
            )[0][1]


        # -------------------------------------------------
        # Convert Prediction
        # -------------------------------------------------

        if prediction == 1:

            result = "Influenza Positive"

        else:

            result = "Influenza Negative"


        # -------------------------------------------------
        # Probability %
        # -------------------------------------------------

        probability_percent = None

        if probability is not None:

            probability_percent = round(
                probability * 100,
                2
            )


        # -------------------------------------------------
        # ส่งผลกลับไปยังหน้าเว็บ
        # -------------------------------------------------

        return render_template(

            "index.html",

            username=session.get(
                "username"
            ),

            result=result,

            probability=probability_percent,

            prediction=int(prediction),

            form_data=request.form

        )


    except Exception as error:

        print("Prediction Error:")
        print(error)


        return render_template(

            "index.html",

            username=session.get(
                "username"
            ),

            error=(
                "เกิดข้อผิดพลาดในการประมวลผล: "
                + str(error)
            )

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