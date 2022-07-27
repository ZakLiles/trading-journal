from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms.fields import EmailField, PasswordField, SubmitField
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# app.jinja_env.undefined = StrictUndefined

class RegisterForm(FlaskForm):
    email = EmailField("Email")
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

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page"""

    form = LoginForm()

    return render_template("login.html", form=form)