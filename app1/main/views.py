from flask import render_template, redirect, url_for, flash, request, session, jsonify
from . import main
from .. import socketio
from .. import db
from ..models import User, Answer
from .forms import RegisterForm, LoginForm, QuestionForm, EditPointsForm, EditTeamForm

from flask_login import login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit


buzzer_status = False
first_user = None

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
    print("user logged out")
    return jsonify({'success': True})


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


@main.route("/admin_page", methods=["GET", "POST"])
def admin_page():
    users = User.query.all()
    global buzzer_status, first_user
    answers = Answer.query.all()
    form = EditPointsForm()
    form1 = EditTeamForm()
    
    return render_template("admin_page.html", users=users, buzzer_status=buzzer_status, first_user=first_user, answers=answers, form=form, form1=form1)


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


@main.route("/buzz", methods=["GET", "POST"])
@login_required
def buzz():
    return render_template("buzz.html", user=current_user)

@main.before_app_first_request
def create_tables():
    db.create_all()
    # new_user = User(username="admin", password="admin")
    # db.session.add(new_user)
    db.session.commit()


def createUser(username, password):
    user = User(username=username, password=password)
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()


def createAnswer(answer):
    answer = Answer(answer=answer, user_id = current_user.id)
    current_user.recent_answer = answer.answer
    db.session.add(answer)
    db.session.commit()


# Socket.IO event for button click
@socketio.on('buzzer_click')
def handle_button_click(user_name):
    global buzzer_status, first_user
    # Check if winner is already set
    if not buzzer_status:
        buzzer_status = True
        first_user = user_name
        # Emit a 'winner' event to the current client only
        emit('winner',user_name,broadcast=True)
    else:
        # Emit a 'loser' event to the current client only
        emit('loser',first_user)

# Socket.IO event for reset button click
@socketio.on('reset_buzzer')
def handle_reset_button_click():
    global buzzer_status, first_user
    print(buzzer_status)
    print("resetting")
    buzzer_status = False
    first_user = ''
    emit('reset',broadcast=True)

@socketio.on('edit_team')
def edit_team(json):
    
    username = json['user_name']
    teamname = json['team_name']
    user = db.one_or_404(
        db.select(User).filter_by(username=username),
        description=f"No user named '{username}'."
    )

    user.team = teamname
    db.session.commit()
    emit('success', broadcast=True)