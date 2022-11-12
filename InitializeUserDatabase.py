import json
import uuid

from flask import Flask, render_template, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt

import ValidateEntries

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = str(uuid.uuid4())
db = SQLAlchemy(app)



@app.route("/register", methods=["GET", "POST"])
def register():
    """verify user's input and register user to database"""
    msg = ""
    test = True
    if request.method == "POST":
        with open("users.json", encoding="utf8") as file:
            users = json.loads(file.read())
        new_user = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "password-verify": request.form.get("password-verify"),
            "email": request.form.get("email")
        }
        test = ValidateEntries.checking_entry(new_user, users["users"])["test"]
        if test:
            users["users"].append(new_user)
            new_user["password"] = sha256_crypt.hash(
                new_user["password"]
            )
            del new_user["password-verify"]
            user_object = json.dumps(users, indent=4)
            with open("users.json", "w", encoding="utf8") as outfile:
                outfile.write(user_object)
            return redirect(url_for("login"))
        if not test:
            msg = ValidateEntries.checking_entry(new_user, users["users"])["msg"]

    return render_template(
        "register.html",
        test=test,
        logged_user=session,
        msg=msg
    )