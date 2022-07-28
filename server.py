from flask import Flask, redirect, render_template, url_for
from flask_wtf import FlaskForm
from wtforms.fields import EmailField, PasswordField, SubmitField, StringField
import os
from jinja2 import StrictUndefined

from model import connect_to_db, db, User

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

app.jinja_env.undefined = StrictUndefined

connect_to_db(app)

class RegisterForm(FlaskForm):
    email = EmailField("Email")
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    password = PasswordField("Password")
    submit = SubmitField("Login")

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

        user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('index'))
    else:
        return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page"""

    form = LoginForm()

    return render_template("login.html", form=form)

if __name__ == "__main__":
    print("connection to DB")
    connect_to_db(app)