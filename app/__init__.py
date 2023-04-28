from flask import Flask
from flask import request
from flask import session
from flask import render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_bootstrap import Bootstrap
from flask_navigation import Navigation
from flask_login import LoginManager
from flask_socketio import SocketIO

login_manager = LoginManager()
login_manager.login_view = "main.login"

db = SQLAlchemy()
socketio = SocketIO()

nav = Navigation()
nav.Bar('top', [
    nav.Item('<i class="bi bi-house-fill" style="font-size: 2rem;"></i>', 'main.home'),
    nav.Item('<i class="bi bi-alarm-fill" style="font-size: 2rem;"></i>', 'main.buzzer'),
    nav.Item('<i class="bi bi-question-lg" style="font-size: 2rem;"></i>', 'main.questions'),
    nav.Item('<i class="bi bi-bar-chart-line-fill" style="font-size: 2rem;"></i>', 'main.leaderboard'),
])



def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    Bootstrap(app)

    socketio.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    nav.init_app(app)
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app