from os import urandom, environ

from flask import Flask, render_template, redirect, url_for

from user import User
from user_management import reporting
from create_groups import create_groups
from models import db, login_manager, logger, sess, env

app = Flask(__name__)
app.register_blueprint(reporting)
app.register_blueprint(create_groups)
app.secret_key = urandom(12)
app.config["SQLALCHEMY_DATABASE_URI"] = env.db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_SQLALCHEMY"] = db
app.config["SESSION_SQLALCHEMY_TABLE"] = "sessions"
# TODO add session timeout
# app.config["SESSION_PERMANENT"] = False
app.config["SESSION_COOKIE_SECURE"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 86400
db.init_app(app)
login_manager.init_app(app)
sess.init_app(app)


@app.route("/401.html")
def error401():
    return render_template("401.html")


@login_manager.user_loader
def user_loader(user_id):
    return db.session.get(User, user_id)


@app.route("/index.html")
@app.route("/index")
@app.route("/")
def index():
    # if current_user.get_id() is not None:
    #     return render_template("index.html", username=current_user.get_id())
    # return render_template("index.html")
    return redirect(url_for("create_groups.create_groups_get"))


if __name__ == "__main__":
    logger.debug(f"Debug: {env.debug}")
    logger.debug(f"Host: {env.host}")
    logger.debug(f"Default Moodle URL: {env.default_moodle_url}")
    logger.debug(f"Default Moodle Service: {env.default_moodle_service}")
    logger.debug(f"DB URI: {env.db_uri}")

    with app.app_context():
        db.create_all()

    app.run(debug=env.debug, host=env.host)
