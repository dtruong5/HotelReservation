import json
import os
import uuid
from datetime import datetime

from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = str(uuid.uuid4())
db = SQLAlchemy(app)

@app.route('/')
def home():
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
