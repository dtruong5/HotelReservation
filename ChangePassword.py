
import json
import uuid

from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt

import ValidateEntries

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = str(uuid.uuid4())
db = SQLAlchemy(app)


@app.route("/update-password", methods=["GET", "POST"])
def change_password():
    """perform checking password and update into new password"""
    msg = ""
    if request.method == "POST":
        with open("users.json") as file:
            users = json.loads(file.read())
        current_password = request.form.get("current-password")
        new_password = request.form.get("new-password")
        verify_password = request.form.get("verify-password")
        password_validated = ValidateEntries.checking_password(
            new_password,
            verify_password
        )["test"]
        pass_correct = sha256_crypt.verify(
            current_password,
            session["hash"]
        )
        if password_validated and pass_correct:
            new_password = sha256_crypt.hash(
                new_password
            )
            session["hash"] = new_password

            for user in users["users"]:
                if user["username"] == session["username"]:
                    user["password"] = new_password
            json_object = json.dumps(users, indent=4)
            with open("users.json", "w", encoding="utf8") as outfile:
                outfile.write(json_object)
        else:
            msg = ValidateEntries.checking_password(
                new_password,
                verify_password
            )["msg"]
    return render_template(
        "update-password.html",
        logged_user=session,
        msg=msg
    )

