import uuid
from datetime import datetime

from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = str(uuid.uuid4())
db = SQLAlchemy(app)


class Todo(db.Model):
    """ Initialize the database, and create our column model """
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}>'

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

