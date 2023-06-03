from user import User
from models import db, logger
from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import current_user, login_user, logout_user

reporting = Blueprint("reporting", __name__)


@reporting.get("/login")
def login():
    return render_template("login.html")


@reporting.post("/login")
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")
    url = request.form.get("moodle_url")
    service = request.form.get("moodle_service")
    try:
        moodle_user = User(username=username, password=password, moodle_url=url,
                           moodle_service=service)
        moodle_user.login()
    except KeyError:
        logger.debug("Moodle Login failed")
        return redirect(url_for("error401"))
    user = User.query.filter_by(username=username).first()
    if user:
        login_user(user)
        user.password = password
        user.moodle_url = url
        user.moodle_service = service
        user.login()
        session["moodle"] = user.moodle.to_json()
        logger.debug("Login success")
        return redirect(url_for("index"))
    else:
        db.session.add(moodle_user)
        db.session.commit()
        login_user(moodle_user)
        logger.debug("Register success")
        return redirect(url_for("index"))


@reporting.route("/logout")
def logout():
    logger.debug("Logout request")
    logout_user()
    return redirect(url_for("index"))

# @reporting.get("/settings")
# def settings():
#     if current_user.get_id() is not None:
#         return render_template("settings.html", username=current_user.get_id(), user=current_user)
#     return redirect(url_for("login"))
#
#
# @reporting.post("/settings")
# def settings_post():
#     if current_user.get_id() is not None:
#         moodle_url = request.form.get("moodle_url")
#         moodle_service = request.form.get("moodle_service")
#         current_user.moodle_url = moodle_url
#         current_user.moodle_service = moodle_service
#         db.session.commit()
#     return redirect(url_for("settings"))
