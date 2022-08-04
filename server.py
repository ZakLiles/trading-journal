from unittest import result
from flask import Flask, redirect, render_template, url_for, flash, session, request
from flask_wtf import FlaskForm
from wtforms.fields import EmailField, PasswordField, SubmitField, StringField, SelectField, FileField
from wtforms.validators import InputRequired, DataRequired, EqualTo
import os
from jinja2 import StrictUndefined
from trades import find_orders, parse_order_row, create_order
from model import connect_to_db, db, User, Trade
from sqlalchemy.sql import func

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
UPLOAD_FOLDER = "static\\files"
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER

app.jinja_env.undefined = StrictUndefined

connect_to_db(app)

class RegisterForm(FlaskForm):
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    email = EmailField("Email", validators=[InputRequired("Email is required!"), DataRequired("Email is required")])
    password = PasswordField("Password", validators=[InputRequired("Password is required!"), DataRequired("Password is required"), EqualTo("password_confirm", message="Passwords must match")])
    password_confirm = PasswordField("Confirm Password", validators=[InputRequired("Password confirmation is required!"), DataRequired("Password is required")])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[InputRequired("Email is required!"), DataRequired("Email is required")])
    password = PasswordField("Password", validators=[InputRequired("Password is required!"), DataRequired("Password is required")])
    submit = SubmitField("Login")

class ImportForm(FlaskForm):
    broker = SelectField("Broker", choices = ["Think or Swim"])
    portfolio = SelectField("Portfolio", choices=["Test Portfolio"])
    time_zone = SelectField("Time Zone", choices=["DO NOT CONVERT", "UTC/GMT -7 US/Mountain"])
    date_format = SelectField("Date Format", choices=["MM/DD/YYYY", "MM/DD/YY", "DD/MM/YY", "YYYY/MM/DD", "YY/MM/DD"])
    trades_file = FileField("File")
    submit = SubmitField("Upload")

@app.route("/")
def index():
    """Home page"""
    user_id = session.get("user_id")
    if user_id:
        trades = Trade.query.filter_by(user_id=user_id).order_by(Trade.open_date).all()
        net_return = db.session.query(func.sum(Trade.return_amt)).filter_by(user_id=user_id).first()[0]
        num_trades = db.session.query(func.count(Trade.return_amt)).filter_by(user_id=user_id).all()[0][0]
        winning_trades = db.session.query(func.count().filter(Trade.result=="WIN").filter(Trade.user_id==user_id)).all()[0][0]
        return render_template("index.html", trades=trades, net_return=net_return, num_trades=num_trades, winning_trades=winning_trades)
    else:
        return render_template("landing.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Registration page"""

    form = RegisterForm()  

    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).all()

        if len(user) == 0:
            user = User(first_name=first_name, last_name=last_name, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful", "success")
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash("This email address is already associated with another account, please use a different email address or sign in with your email.")
            return render_template("register.html", form=form)
    if form.errors:
        flash("{}".format(form.errors), "danger")

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page"""

    form = LoginForm()

    if form.validate_on_submit():

        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user is None:
            flash("No user with associate e-mail exists. Please complete registration", "danger")
            return redirect(url_for("index"))
        if user.check_password(password):
            print("Password matches")
            flash("You are successfully logged in.", "success")
            login_user(user)
            return redirect(url_for("index"))
        else: 
            flash("Password is incorrect, please try again", "danger")
            form.password.errors.append("Incorrect Password")

    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    """Logout"""

    if not session.get("user_id"):
        flash("You are not logged in")
    else:
        logout_user()
        flash("You are logged out", "success")
    return redirect(url_for("index"))

@app.route("/add-trades", methods=["GET", "POST"])
def import_trades():
    """Import trades from CSV"""
    
    form = ImportForm()

    if form.validate_on_submit():

        uploaded_file = request.files['trades_file']
        if uploaded_file.filename != '':

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)

            uploaded_file.save(file_path)
            orders_list = find_orders(file_path)
            user_id = session["user_id"]

            for order in orders_list:
                exec_time, spread, side, qty, pos_effect, symbol, expiration, strike_price, type, price, order_type = parse_order_row(order)
                create_order(user_id=user_id, exec_time=exec_time, spread=spread, side=side, qty=qty, pos_effect=pos_effect, symbol=symbol, expiration=expiration, strike_price=strike_price, type=type, price=price,order_type=order_type)
            
            flash("Trades uploaded successfully", "success")
            return redirect(url_for("index"))

    return render_template("import.html", form=form)


def login_user(user):
    session["user_id"] = user.user_id

def logout_user():
    session.pop("user_id")

if __name__ == "__main__":
    print("connection to DB")
    connect_to_db(app)