
from datetime import datetime, date
import os
import json
import uuid

import requests
from flask import Flask, render_template, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = str(uuid.uuid4())
db = SQLAlchemy(app)


def logger(username):
    """
        keep a log of all fail log in attempts under users.json
    """
    with open("users.json", encoding="utf8") as file:
        users = json.loads(file.read())
        for user in users["users"]:
            if user["username"] == username:
                if "attempts" in user.keys():
                    user["attempts"].append({
                        "date": str(date.today()),
                        "time": str(datetime.now().strftime("%H:%M:%S")),
                        "ip": request.remote_addr
                    })
                else:
                    user["attempts"] = [{
                        "date": str(date.today()),
                        "time": str(datetime.now().strftime("%H:%M:%S")),
                        "ip": request.remote_addr
                    }]
        print(requests.get("https://ip.42.pl/raw").text)
        json_object = json.dumps(users, indent = 4)
        with open("users.json", "w", encoding="utf8") as outfile:
            outfile.write(json_object)

