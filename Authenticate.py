import json
import os
import uuid
from datetime import datetime

import LogMonitor
import ValidateEntries
from flask import Flask, render_template, request, url_for, redirect, session
from flask_wtf import FlaskForm
from wtforms import validators, SubmitField
from wtforms.fields import DateField
from flask_classful import FlaskView, route
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = str(uuid.uuid4())
db = SQLAlchemy(app)

class InfoForm(FlaskForm):
    startdate = DateField('Start Date', format='%Y-%m-%d', validators=(validators.DataRequired(),))
    enddate = DateField('End Date', format='%Y-%m-%d', validators=(validators.DataRequired(),))
    submit = SubmitField('Submit')

class LogUserOut(FlaskView):
    def logout(self):
        """logging off"""
        session["username"] = ""
        session["hash"] = ""
        session["logged"] = False
        return render_template(
            "main_page.html",
            logged_user=session
        )


class LogUserIn(FlaskView):
    default_methods = ['GET', 'POST']

    def login(self):
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
                    return redirect(url_for("Gallery:note"))
            msg = "Incorrect username or password, please try again"
            LogMonitor.logger(data["username"])

        return render_template(
            "login.html",
            logged_user=session,
            msg=msg
        )


class UpdateUserPassword(FlaskView):
    @route('/update_password/', methods=['GET', 'POST'])
    def update_password(self):
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
            "update_password.html",
            logged_user=session,
            msg=msg
        )


class Registration(FlaskView):
    @route('/register/', methods=['GET', 'POST'])
    def registerUser(self):
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
                return redirect(url_for("LogUserIn:login"))
            if not test:
                msg = ValidateEntries.checking_entry(new_user, users["users"])["msg"]

        return render_template(
            "register.html",
            test=test,
            logged_user=session,
            msg=msg
        )


@app.route('/')
def home():
    """ set the default home page """
    return render_template(
        'main_page.html',
        logged_user=session
    )


class Gallery(FlaskView):
    def note(self):
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


class Receptionist(FlaskView):
    default_methods = ["GET", "POST"]

    def comments(self):
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


class Init_db(db.Model):
    """ Initialize the database, and create our column model """
    id = db.Column(db.Integer, primary_key=True)
    num_of_adult = db.Column(db.Integer, nullable=False)
    check_in_date = db.Column(db.String(200), nullable=False)
    check_out_date = db.Column(db.String(200), nullable=False)
    room = db.Column(db.String(200), nullable=False)
    def __repr__(self):
        return f'<Task {self.id}>'


class Reservation(FlaskView):
    default_methods = ["GET", "POST"]

    def task(self):
        """store the content from task manager to database"""
        form = InfoForm()
        if request.method == 'POST':
            new_task = Init_db(num_of_adult=request.form.get('number_of_guests'), check_in_date=form.startdate.data, check_out_date=form.enddate.data,
                               room=request.form.get('room'))
            try:
                db.session.add(new_task)
                db.session.commit()

                return redirect('/task')
            except(RuntimeError, ValueError, NameError):
                return 'There was an issue adding your task'
        else:
            tasks = Init_db.query.order_by(Init_db.check_out_date).all()
            return render_template(
                'index.html',
                form=form,
                tasks=tasks,
                logged_user=session
            )

    @route('/delete/<int:identification>')
    def delete(self, identification):
        """ provide the function to delete task from database """
        task_to_delete = Init_db.query.get_or_404(identification)
        try:
            db.session.delete(task_to_delete)
            db.session.commit()
            return redirect('/task')
        except(RuntimeError, ValueError, NameError):
            return 'There was a problem deleting that task'

    @route('/update/<int:identification>', methods=['GET', 'POST'])
    def update(self, identification):
        """update the task that already exist in the database"""
        task = Init_db.query.get_or_404(identification)
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
@app.route('/date', methods=['GET', 'POST'])
def date():
    startdate = session['startdate']
    enddate = session['enddate']
    return render_template('date.html')



LogUserIn.register(app, route_base='/')
LogUserOut.register(app, route_base='/')
Gallery.register(app, route_base='/')
Receptionist.register(app, route_base='/')
Registration.register(app, route_base='/')
Reservation.register(app, route_base='/')
UpdateUserPassword.register(app, route_base='/')

if __name__ == "__main__":
    db.drop_all()
    db.create_all()
    app.run()
