
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


def checking_password(password, verify_password):
    """
        checking for password requirements
    """
    test = True
    msg = ""
    count = 0
    for char in password:
        if char in "[@_!#$%^&*()<>?/|}{~:=]":
            count = count + 1
            print(password)
            print(count)
    if count == 0:
        test = False
        msg = "Passwords need at least one special character"
        print(password)
        print(count)
    if len(password) < 12:
        test = False
        msg = "Passwords need at least 12 characters"

    if not any(char.isdigit() for char in password):
        test = False
        msg = "Passwords need at least one number"
    if not any(char.isupper() for char in password):
        test = False
        msg = "Password need at least one upper character"
    if not any(char.islower() for char in password):
        test = False
        msg = "Password need at least one lower character"
    if not password == verify_password:
        test = False
        msg = "Password did not match"

    with open("CommonPassword.txt", encoding="utf8") as file:
        for word in file:
            if password == word.strip().lower():
                test = False
                msg = "Please choose another password"
    return {
        "test": test,
        "msg": msg
    }


def checking_entry(data, users):
    """
        checking user's submission entry
    """
    test = checking_password(
        data["password"],
        data["password-verify"]
    )["test"]
    msg = checking_password(
        data["password"],
        data["password-verify"]
    )["msg"]
    if not test:
        test = False
    if not "@" in data["email"]:
        test = False
        msg = "Please enter a valid email address"
    if data["username"] == "":
        test = False
        msg = "Please enter a username"
    for user in users:
        if user["username"].lower() == data["username"].lower():
            test = False
            msg = "that username is already taken"
    return {
        "test": test,
        "msg": msg
    }
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
        password_validated = checking_password(
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
            msg = checking_password(
                new_password,
                verify_password
            )["msg"]
    return render_template(
        "update-password.html",
        logged_user=session,
        msg=msg
    )


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
        logger(data["username"])

    return render_template(
        "login.html",
        logged_user=session,
        msg=msg
    )


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
        test = checking_entry(new_user, users["users"])["test"]
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
            msg = checking_entry(new_user, users["users"])["msg"]

    return render_template(
        "register.html",
        test=test,
        logged_user=session,
        msg=msg
    )


class Todo(db.Model):
    """ Initialize the database, and create our column model """
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}>'


@app.route('/')
def main_page():
    """ set the default home page """
    return render_template(
        'main_page.html',
        logged_user=session
    )


@app.route('/note')
def note():
    """Get the content from post and displaying them on route /note"""
    titles = os.listdir('./posts')
    posts = []

    for title in titles:
        with open('./posts/' + title, encoding="utf8") as file:
            file_contents = file.read()
            posts.append({
                'title': title,
                'content': file_contents
            })

    posts.reverse()

    return render_template(
        'note.html',
        posts=posts,
        logged_user=session
    )


@app.route('/comments', methods=["GET", "POST"])
def comments():
    """gets content from comments.json"""

    with open('comments.json', encoding="utf8") as file:
        string = json.loads(file.read())

    if request.method == 'POST':
        string['comments'].append({
            "name": request.form.get("name"),
            "message": request.form.get("message"),
            "date": datetime.now().strftime("%B %d, %Y - %H:%M")
        })

        json_object = json.dumps(string, indent=4)
        with open("comments.json", "w", encoding="utf8") as outfile:
            outfile.write(json_object)

    return render_template(
        'comments.html',
        comments=string['comments'],
        logged_user=session
    )


@app.route('/task', methods=['POST', 'GET'])
def index():
    """store the content from task manager to database"""
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/task')
        except(RuntimeError, ValueError, NameError):
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template(
            'index.html',
            tasks=tasks,
            logged_user=session
        )


@app.route('/delete/<int:identification>')
def delete(identification):
    """ provide the function to delete task from database """
    task_to_delete = Todo.query.get_or_404(identification)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/task')
    except(RuntimeError, ValueError, NameError):
        return 'There was a problem deleting that task'


@app.route('/update/<int:identification>', methods=['GET', 'POST'])
def update(identification):
    """update the task that already exist in the database"""
    task = Todo.query.get_or_404(identification)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/task')
        except(RuntimeError, ValueError, NameError):
            return 'There was an issue updating your task'

    else:
        return render_template(
            'update.html',
            task=task,
            logged_user=session
        )


if __name__ == "__main__":
    db.create_all()
    app.run()
