import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash


load_dotenv()

from flask_sqlalchemy import SQLAlchemy
SQL_ALCHEMY_DATABASE_URI = os.getenv('SQL_ALCHEMY_DATABASE_URI')

db = SQLAlchemy()

class User(db.Model):
    """Trader info"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    pass_hash = db.Column(db.String(255), nullable=False)

    def __init__(self, email, first_name, last_name, password):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.pass_hash = generate_password_hash(password)


class Trade(db.Model):
    """Trade info"""

    __tablename__ = "trade"

    trade_id = db.Column(db.Integer, autoincrement = True, primary_key=True)

def connect_to_db(app):
    """Connect the database to the Flask app"""

    app.config['SQLALCHEMY_DATABASE_URI'] = SQL_ALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

if __name__ == "__main__":
    from server import app
    connect_to_db(app)

    db.create_all()
