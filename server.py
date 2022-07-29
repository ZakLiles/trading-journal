from flask import Flask, redirect, render_template, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms.fields import EmailField, PasswordField, SubmitField, StringField
from wtforms.validators import InputRequired, DataRequired, EqualTo
import os
from jinja2 import StrictUndefined

from model import connect_to_db, db, User

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

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
    email = EmailField("Email")
    password = PasswordField("Password")
    submit = SubmitField("Login")

@app.route("/")
def index():
    """Home page"""

    return render_template("index.html")

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
            flash("Registration succesful", "success")
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

    return render_template("login.html", form=form)

def login_user(user):
    session["user_id"] = user.user_id

def logout_user():
    session.pop("user_id")

if __name__ == "__main__":
    print("connection to DB")
    connect_to_db(app)