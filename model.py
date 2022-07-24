import os
from dotenv import load_dotenv

load_dotenv()

from flask_sqlalchemy import SQLAlchemy
SQL_ALCHEMY_DATABASE_URI = os.getenv('SQL_ALCHEMY_DATABASE_URI')

db = SQLAlchemy()

class User(db.Model):
    """Trader info"""

    __tablename__ = "users"


class Trade(db.Model):
    """Trade info"""

    __tablename__ = "trade"