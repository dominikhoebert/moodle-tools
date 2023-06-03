from user import User
from models import db, logger
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import current_user
from moodle_sync_testing import MoodleSyncTesting

create_groups = Blueprint("create_groups", __name__)


@create_groups.get("/create-groups")
def create_groups_get():
    flash("This feature is not yet implemented", "warning")
    if current_user.get_id() is not None:
        if type(moodle_json := session.get("moodle", None)) is dict:
            current_user.moodle = MoodleSyncTesting.from_json(moodle_json)
        return render_template("create_groups.html", username=current_user.get_id())
    return redirect(url_for("reporting.login"))
