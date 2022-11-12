import uuid

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = str(uuid.uuid4())
db = SQLAlchemy(app)

if __name__ == "__main__":
    db.create_all()
    app.run()
