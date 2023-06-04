from os import urandom

from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import current_user

from user import User
from user_management import reporting
from todo import todo
from create_groups import create_groups
from models import db, login_manager, logger, sess
from moodle_sync_testing import MoodleSyncTesting

app = Flask(__name__)
app.register_blueprint(reporting)
app.register_blueprint(todo)
app.register_blueprint(create_groups)
app.secret_key = urandom(12)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_SQLALCHEMY"] = db
app.config["SESSION_SQLALCHEMY_TABLE"] = "sessions"
#TODO add session timeout
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_COOKIE_SECURE"] = True
#app.config["PERMANENT_SESSION_LIFETIME"] = 86400
db.init_app(app)
login_manager.init_app(app)
sess.init_app(app)


@app.route("/401.html")
def error401():
    return render_template("401.html")


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


@app.route("/index.html")
@app.route("/index")
@app.route("/")
def index():
    if current_user.get_id() is not None:
        return render_template("index.html", username=current_user.get_id())
    return render_template("index.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
