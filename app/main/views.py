from flask import render_template, redirect, url_for, flash, request, session, jsonify
from . import main
from .. import socketio
from .. import db
from ..models import User, Answer
from .forms import RegisterForm, LoginForm, QuestionForm, EditPointsForm

from flask_login import login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit


buzzer_status = False
first_user = None

winner = {'username': None}


@main.route("/")
def index():
    return redirect(url_for("main.home"))


@main.route("/home")
def home():
    return render_template("index.html")


@main.route("/login", methods=["GET", "POST"])
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
        return redirect(url_for("main.questions"))

    return render_template("login.html", form=form)


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegisterForm()
    if (form.validate_on_submit()):
        username = form.username.data
        password = form.password.data
        # password = generate_password_hash(password)
        createUser(username, password)
        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)


@main.route("/logout", methods=["GET", "POST"])
def logout():
    current_user.authenticated = False
    logout_user()
    return render_template("index.html")


@main.route("/questions", methods=["GET", "POST"])
@login_required
def questions():
    form = QuestionForm()
    if (form.validate_on_submit()):
        answer = form.answer.data
        createAnswer(answer)
    return render_template("questions.html", form=form)


@main.route("/leaderboard", methods=["GET", "POST"])
def leaderboard():
    users = User.query.order_by(User.points.desc()).all()
    return render_template("leaderboard.html", users=users)


@main.route("/pressed", methods=["GET", "POST"])
def pressed():
    global buzzer_status, first_user
    if not buzzer_status:
        buzzer_status = True
        first_user = current_user
        return render_template("buzzer.html", buzzer_status=buzzer_status, first_user=first_user)
    else:
        return render_template("buzzer.html", buzzer_status=buzzer_status, first_user=first_user)


@main.route("/buzzer", methods=["GET", "POST"])
@login_required
def buzzer():
    global buzzer_status, first_user
    return render_template("buzzer.html", buzzer_status=buzzer_status, first_user=first_user, username=current_user.username)


@main.route("/admin_page", methods=["GET", "POST"])
def admin_page():
    users = User.query.all()
    global buzzer_status, first_user
    answers = Answer.query.all()
    form = EditPointsForm()
    
    return render_template("admin_page.html", users=users, buzzer_status=buzzer_status, first_user=first_user, answers=answers, form=form)

@main.route('/edit_points/<int:id>', methods=['POST'])
def edit_points(id):
    user = User.query.get(id)
    form = EditPointsForm()

    if form.validate_on_submit():
        points = int(form.points.data)
        user.points += points
        db.session.commit()

    return redirect(url_for('main.admin_page'))

@main.route("/<username>", methods=["GET", "POST"])
@login_required
def profile(username):
    user = db.one_or_404(
        db.select(User).filter_by(username=username),
        description=f"No user named '{username}'."
    )
    answers = Answer.query.filter_by(user_id=user.id).all()
    return render_template("profile.html", user=user, answers=answers)


@main.before_app_first_request
def create_tables():
    db.create_all()
    # new_user = User(username="admin", password="admin")
    # db.session.add(new_user)
    db.session.commit()


def createUser(username, password):
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()


def createAnswer(answer):
    answer = Answer(answer=answer, user_id = current_user.id)
    db.session.add(answer)
    db.session.commit()


@main.route("/resetBuzzer", methods=["GET", "POST"])
def resetBuzzer():
    global buzzer_status, first_user
    buzzer_status = False
    first_user = None
    users = User.query.all()
    answers = Answer.query.all()
    
    form = EditPointsForm()
    return render_template("admin_page.html", users=users, buzzer_status=buzzer_status, first_user=first_user, answers=answers,form=form)

@main.route("/buzz", methods=["GET", "POST"])
def buzz():
    return render_template("buzz.html")

# Socket.IO event for button click
@socketio.on('button_click')
def handle_button_click(data):
    # Check if winner is already set
    if winner['username'] is None:
        # Update winner with the username of the current user
        winner['username'] = data['username']
        # Emit a 'winner' event to the current client only
        emit('winner', {'username': data['username']})
    else:
        # Emit a 'loser' event to the current client only
        emit('loser')