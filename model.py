import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

from flask_sqlalchemy import SQLAlchemy
SQL_ALCHEMY_DATABASE_URI = os.getenv('SQL_ALCHEMY_DATABASE_URI')

db = SQLAlchemy()

class User(db.Model):
    """User info"""

    __tablename__ = "user"

    user_id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    pass_hash = db.Column(db.String(255), nullable=False)
    trade = db.relationship("Trade", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, email, first_name, last_name, password):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.pass_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pass_hash, password)

class Trade(db.Model):
    """Trade info"""

    __tablename__ = "trade"

    trade_id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.user_id"), nullable=False)
    user = db.relationship("User", back_populates="trade")
    open_date = db.Column(db.DateTime())
    symbol = db.Column(db.String(10))
    entry_price = db.Column(db.Float())
    exit_price = db.Column(db.Float())
    return_amt = db.Column(db.Float(), default = 0)
    result = db.Column(db.String(10))
    side = db.Column(db.String(10))
    spread = db.Column(db.String(10))
    order = db.relationship("Order", back_populates="trade")
    open = db.Column(db.Boolean(), default=True)
    position = db.Column(db.Integer())

    def __init__(self, user_id, open_date, symbol, entry_price, side, spread, position):
        self.user_id = user_id
        self.open_date = open_date
        self.symbol = symbol
        self.entry_price = entry_price
        self.side = side
        self.spread = spread
        self.position = position

    def __repr__(self):
        return f'Trade(trade_id={self.trade_id}, symbol={self.symbol}, open_date={self.open_date}, side={self.side}, spread={self.spread}, open={self.open})'

class Order(db.Model):
    """Order info"""

    __tablename__ = "order"

    order_id = db.Column(db.Integer(), autoincrement = True, primary_key=True)
    trade_id = db.Column(db.Integer(), db.ForeignKey("trade.trade_id"), nullable=False)
    exec_time = db.Column(db.DateTime())
    spread = db.Column(db.String(10))
    side = db.Column(db.String(10))
    qty = db.Column(db.Integer())
    pos_effect = db.Column(db.String(10))
    symbol = db.Column(db.String(10))
    expiration = db.Column(db.DateTime())
    strike_price = db.Column(db.Float())
    type = db.Column(db.String(10))
    price = db.Column(db.Float())
    order_type = db.Column(db.String(10))
    setup = db.Column(db.String())
    trade = db.relationship("Trade", back_populates="order")

    def __init__(self, trade_id, exec_time, spread, side, qty, pos_effect, symbol, expiration, strike_price, type, price, order_type):
        self.trade_id = trade_id
        self.exec_time = exec_time
        self.spread = spread
        self.side = side
        self.qty = qty
        self.pos_effect = pos_effect
        self.symbol = symbol
        self.expiration = expiration
        self.strike_price = strike_price
        self.type = type
        self.price = price
        self.order_type = order_type

    def __repr__(self):
        return f'Order(trade_id={self.trade_id}, symbol={self.symbol}, exec_time={self.exec_time}, side={self.side}, spread={self.spread}, pos_effect={self.pos_effect})'

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
