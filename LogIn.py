import json
import uuid

from flask import Flask, render_template, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt

import LoggingUser

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = str(uuid.uuid4())
db = SQLAlchemy(app)


@app.route("/login", methods=["GET", "POST"])
def login():
    """logging in"""
    msg = ""
    if request.method == "POST":
        with open("users.json", encoding="utf8") as file:
            users = json.loads(file.read())
        data = {
            "username": request.form.get("username"),
            "password": request.form.get("password")
        }
        for user in users["users"]:
            user_matching = data["username"].lower() == user["username"].lower()
            password_match = sha256_crypt.verify(
                data["password"],
                user["password"]
            )
            if user_matching and password_match:
                session["username"] = user["username"]
                session["hash"] = user["password"]
                session["logged"] = True
                return redirect(url_for("note"))
        msg = "Incorrect username or password, please try again"
        LoggingUser.logger(data["username"])

    return render_template(
        "login.html",
        logged_user=session,
        msg=msg
    )
