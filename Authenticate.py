#!/usr/bin/env python3

import json
import random
import string
import time
import uuid
from datetime import datetime

from flask import Flask, render_template, request, url_for, redirect, session
from flask_classful import FlaskView, route
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from passlib.hash import sha256_crypt
from waitress import serve
from wtforms import validators, SubmitField
from wtforms.fields import DateField

import LogMonitor
import ValidateEntries

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hotel.db'
app.secret_key = str(uuid.uuid4())
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
PORT = 8080


class Hotel(db.Model):
    """ initialize the database, and create our column model """
    id = db.Column(db.Integer, primary_key=True)
    num_of_adult = db.Column(db.Integer, nullable=False)
    check_in_date = db.Column(db.String(200), nullable=False)
    check_out_date = db.Column(db.String(200), nullable=False)
    room = db.Column(db.String(200), nullable=False)

    def __init__(self, num_of_adult, check_in_date, check_out_date, room):
        self.num_of_adult = num_of_adult
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.room = room

    def __repr__(self):
        return f'<Hotel {self.id}>'


class InfoForm(FlaskForm):
    startdate = DateField('Start Date', format='%Y-%m-%d',
                          validators=(validators.DataRequired(),))
    enddate = DateField('End Date', format='%Y-%m-%d',
                        validators=(validators.DataRequired(),))
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
                user_matching = data["username"].lower(
                ) == user["username"].lower()
                password_match = sha256_crypt.verify(
                    data["password"],
                    user["password"]
                )
                if user_matching and password_match:
                    session["username"] = user["username"]
                    session["hash"] = user["password"]
                    session["logged"] = True
                    return redirect(url_for("Gallery:show_rooms"))
            msg = "Incorrect username or password, please try again"
            LogMonitor.logger(data["username"])

        return render_template(
            "login.html",
            logged_user=session,
            msg=msg
        )


class UpdateUserPassword(FlaskView):
    global email
    global sent_code
    email = ''
    sent_code = ''

    @route('/update_password/', methods=['GET', 'POST'])
    def update_password(self):
        """perform checking password and update into new password"""
        self.startstart = 0.0
        self.stop = 0.0

        sent_em = False
        msg = ""
        errmsg = ''
        resetmsg = ''

        if request.method == "POST":
            if "form1" in request.form:
                email1 = request.form.get("email")

                with open("users.json", encoding="utf8") as file:
                    users = json.loads(file.read())
                    found = False
                    for user in users["users"]:
                        if user['email'] == email1:
                            found = True
                    if found:
                        sent_em = True
                        # generating random strings
                        N = 7
                        res = ''.join(random.choices(
                            string.ascii_uppercase + string.digits, k=N))
                        global sent_code
                        sent_code = res
                        global email
                        email = email1
                    if not found:
                        return ('Email not found. Please refresh the page and again.')

            if "form2" in request.form:
                stop = time.perf_counter()
                self.stop = stop
                elapsedtime = (self.start-self.stop)

                if elapsedtime > -30.0:
                    ver_code = request.form.get("verification-code")
                    new_password = request.form.get("new-password")
                    verify_password = request.form.get("verify-password")

                    if ver_code == sent_code:
                        validpwd = ValidateEntries.checking_password(
                            new_password, verify_password)

                        if validpwd["valid_pwd"] == True:
                            new_pass = sha256_crypt.hash(verify_password)
                            f = open('users.json',)
                            data = json.load(f)

                            for user in data["users"]:
                                if user["email"] == email:
                                    user.update({'password': new_pass})
                            data = json.dumps(data, indent=4)
                            with open("users.json", "w", encoding="utf8") as outfile:
                                outfile.write(data)
                                f.close()
                                outfile.close()
                            return redirect(url_for("LogUserIn:login"))

                        if validpwd["valid_pwd"] == False:
                            resetmsg = validpwd['msg']
                            sent_em = True
                    if ver_code != sent_code:
                        return "The verication code does not match. Please refresh the page and try again."

                if elapsedtime < -30.0:
                    print('1')
                    errmsg = "You must enter the code with 60 seconds. Please try again."
                    errmsg = errmsg

            if sent_em == True:
                print('email sent')
                self.start = time.perf_counter()

        return render_template(
            "update_password.html",
            logged_user=session,
            msg=msg,
            sent_em=sent_em,
            sent_code=sent_code,
            errmsg=errmsg,
            resetmsg=resetmsg
        )


class Registration(FlaskView):
    @route('/register/', methods=['GET', 'POST'])
    def registerUser(self):
        """verify user's input and register user to database"""
        user_validated = False
        msg = ''

        if request.method == "POST":
            with open("users.json", encoding="utf8") as file:
                users = json.loads(file.read())
            new_user = {
                "username": request.form.get("username"),
                "password": request.form.get("password"),
                "password-verify": request.form.get("password-verify"),
                "email": request.form.get("email")
            }
            validate_user = ValidateEntries.checking_entry(new_user, users)
            user_validated = validate_user['valid-user']
            msg = validate_user['msg']

            if user_validated:
                users["users"].append(new_user)
                new_user["password"] = sha256_crypt.hash(
                    new_user["password"]
                )
                del new_user["password-verify"]
                user_object = json.dumps(users, indent=4)
                with open("users.json", "w", encoding="utf8") as outfile:
                    outfile.write(user_object)
                return redirect(url_for("LogUserIn:login"))
            if not user_validated:
                user_validated = user_validated
        return render_template(
            "register.html",
            user_validated=user_validated,
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
    def show_rooms(self):
        """ show images of rooms in a table """

        return render_template(
            'gallery.html',
            logged_user=session
        )


class Receptionist(FlaskView):  # Bookings Tab
    default_methods = ["GET", "POST"]

    def bookings(self):
        """gets content from bookings.json"""

        with open('bookings.json', encoding="utf8") as file:
            string = json.loads(file.read())

        if request.method == 'POST':
            string['bookings'].append({
                "name": request.form.get("name"),
                "message": request.form.get("message"),
                "date": datetime.now().strftime("%B %d, %Y - %H:%M")
            })

            json_object = json.dumps(string, indent=4)
            with open("bookings.json", "w", encoding="utf8") as outfile:
                outfile.write(json_object)

        return render_template(
            'bookings.html',
            bookings=string['bookings'],
            logged_user=session
        )


class Reservation(FlaskView):
    default_methods = ["GET", "POST"]

    def reservation(self):
        """store the content from task manager to database"""
        form = InfoForm()
        if request.method == 'POST':
            new_task = Hotel(num_of_adult=request.form.get('number_of_guests'), check_in_date=form.startdate.data, check_out_date=form.enddate.data,
                             room=request.form.get('room'))
            try:
                db.session.add(new_task)
                db.session.commit()

                return redirect('/reservation')
            except (RuntimeError, ValueError, NameError):
                return 'There was an issue adding your task'
        else:
            tasks = Hotel.query.order_by(Hotel.check_out_date).all()
            return render_template(
                'index.html',
                form=form,
                tasks=tasks,
                logged_user=session
            )

    @route('/delete/<int:identification>')
    def delete(self, identification):
        """ provide the function to delete task from database """
        task_to_delete = Hotel.query.get_or_404(identification)
        try:
            db.session.delete(task_to_delete)
            db.session.commit()
            return redirect('/reservation')
        except (RuntimeError, ValueError, NameError):
            return 'There was a problem deleting that task'

    @route('/update/<int:identification>', methods=['GET', 'POST'])
    def update(self, identification):
        form = InfoForm
        """update the task that already exist in the database"""
        task = Hotel.query.get_or_404(identification)
        if request.method == 'POST':
            task.num_of_adult = request.form.get('num_of_adult')
            task.check_in_date = request.form.get('check_in_date')
            task.check_out_date = request.form.get('check_out_date')
            task.room = request.form.get('room')
            try:
                db.session.commit()
                return redirect('/reservation')
            except (RuntimeError, ValueError, NameError):
                return 'There was an issue updating your task'
        else:
            return render_template(
                'update.html',
                form=form,
                task=task,
                logged_user=session
            )


LogUserIn.register(app, route_base='/')
LogUserOut.register(app, route_base='/')
Gallery.register(app, route_base='/')
Receptionist.register(app, route_base='/')
Registration.register(app, route_base='/')
Reservation.register(app, route_base='/')
UpdateUserPassword.register(app, route_base='/')


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    #app.run(debug = True)
    serve(app, host='0.0.0.0', port=PORT)
