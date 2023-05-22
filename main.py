from os import urandom

from flask import Flask, render_template, request, redirect, url_for
from flask_login import current_user

from user import User
from user_management import reporting
from todo import todo
from models import db, login_manager, logger

app = Flask(__name__)
app.register_blueprint(reporting)
app.register_blueprint(todo)
app.secret_key = urandom(12)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
login_manager.init_app(app)


@app.route("/401.html")
def error401():
    logger.debug("401 request")
    return render_template("401.html")


@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve

    """
    return User.query.get(user_id)

@app.route("/index.html")
@app.route("/index")
@app.route("/")
def index():
    """For GET requests, display the registration form. For POSTS, register the new user.

    """

    logger.debug("Index request")
    logger.debug(current_user)
    logger.debug(current_user.is_authenticated)
    logger.debug(current_user.get_id())
    if current_user.get_id() is not None:
        return render_template("index.html", username=current_user.get_id())
    return render_template("index.html")


if __name__ == "__main__":
    # with app.app_context():
    #    db.create_all()

    app.run(debug=True)
