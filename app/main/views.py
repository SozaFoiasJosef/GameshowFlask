from flask import session
from flask import render_template, redirect, url_for, flash, request
from . import main
from .. import db
from ..models import User, Answer
from .forms import RegisterForm, LoginForm, QuestionForm

from flask_login import login_user, logout_user, login_required, current_user



@main.route("/")
def index():
    return redirect(url_for("main.home"))

@main.route("/home")
def home():
    return render_template("index.html")

@main.route("/login", methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.questions"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("main.login"))
        login_user(user, remember=True)
        session["username"] = user.username
        return redirect(url_for("questions"))
        
    return render_template("login.html", form=form)

@main.route("/register", methods = ["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegisterForm()
    if(form.validate_on_submit()):
        username = form.username.data
        password = form.password.data
        email = form.email.data
        ##password = generate_password_hash(password)
        createUser(username, password, email)
        return redirect(url_for("main.login"))
        
    return render_template("register.html", form=form)

@main.route("/logout", methods = ["GET", "POST"])
def logout():
    current_user.authenticated = False
    logout_user()
    return render_template("logout.html")

@main.route("/questions", methods = ["GET", "POST"])
@login_required
def questions():
    form = QuestionForm()
    if(form.validate_on_submit()):
        answer = form.answer.data
        createAnswer(answer)
    return render_template("questions.html")

@main.route("/database", methods = ["GET", "POST"])
def database():
    users = User.query.all()
    return render_template("database.html", users=users)

def createUser(username, password, email):
    user = User(username=username, password=password, email=email)
    db.session.add(user)
    db.session.commit()

def createAnswer(answer):
    answer = Answer(answer=answer)
    db.session.add(answer)
    db.session.commit()
