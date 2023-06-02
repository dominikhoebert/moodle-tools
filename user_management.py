from user import User
from models import db, logger
from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import current_user, login_user, logout_user

reporting = Blueprint("reporting", __name__)


# @reporting.get("/register")
# def register():
#     return render_template("register.html")
#
#
# @reporting.post("/register")
# def register_post():
#     email = request.form.get("email")
#     password = request.form.get("password")
#     password_confirm = request.form.get("passwordconfirm")
#     logger.debug(f"email: {email}, password: {password}, password_confirm: {password_confirm}")
#     if password != password_confirm:
#         logger.debug("Register failed, password not matching")
#         # TODO: add error message, keep email address in form
#         return redirect(url_for("register"))
#     user = User.query.filter_by(email=email).first()
#     if user:
#         logger.debug("Register failed")
#         return redirect(url_for("error401"))
#     else:
#         new_user = User(email=email, password=password, authenticated=False)
#         db.session.add(new_user)
#         db.session.commit()
#         logger.debug("Register success")
#         return redirect(url_for("index"))


@reporting.get("/login")
def login():
    return render_template("login.html")


@reporting.post("/login")
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")
    logger.debug(f"username: {username}, password: {password}")
    user = User.query.filter_by(username=username).first()
    if user:
        if user.password == password:
            login_user(user)
            user.login()
            session["moodle"] = user.moodle.to_json()
            logger.debug("Login success")
            return redirect(url_for("index"))
        else:
            logger.debug("Login failed")
            return redirect(url_for("error401"))
    else:
        try:
            user = User(username=username, password=password, moodle_url="https://elearning.tgm.ac.at",
                        moodle_service="tgm_hoedmoodlesync")
            user.login()
        except KeyError:
            logger.debug("Register failed")
            return redirect(url_for("error401"))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        logger.debug("Register success")
        return redirect(url_for("index"))


@reporting.route("/logout")
def logout():
    logger.debug("Logout request")
    logout_user()
    return redirect(url_for("index"))


@reporting.get("/settings")
def settings():
    if current_user.get_id() is not None:
        return render_template("settings.html", username=current_user.get_id(), user=current_user)
    return redirect(url_for("login"))


@reporting.post("/settings")
def settings_post():
    if current_user.get_id() is not None:
        moodle_url = request.form.get("moodle_url")
        moodle_service = request.form.get("moodle_service")
        current_user.moodle_url = moodle_url
        current_user.moodle_service = moodle_service
        db.session.commit()
    return redirect(url_for("settings"))
