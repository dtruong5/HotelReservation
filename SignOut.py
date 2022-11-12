import uuid
from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = str(uuid.uuid4())
db = SQLAlchemy(app)

@app.route("/logout")
def logout():
    """logging off"""
    session["username"] = ""
    session["hash"] = ""
    session["logged"] = False
    return render_template(
        "main_page.html",
        logged_user=session
    )

