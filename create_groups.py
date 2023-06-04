from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import current_user
from moodle_sync_testing import MoodleSyncTesting
import pandas as pd
import io

from models import logger

create_groups = Blueprint("create_groups", __name__, url_prefix="/create-groups")

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@create_groups.get("/")
def create_groups_get():
    if current_user.get_id() is not None:
        if type(moodle_json := session.get("moodle", None)) is dict:
            current_user.moodle = MoodleSyncTesting.from_json(moodle_json)
            logger.debug(current_user.moodle.students)
            #if current_user.moodle.students is not None:
        return render_template("create_groups.html", username=current_user.get_id(),
                               students=current_user.moodle.students)
    return redirect(url_for("reporting.login"))


@create_groups.post("/file-upload")
def file_upload():
    if 'file' not in request.files:
        flash('No file part')
        logger.debug("No file part")
        return redirect(url_for('create_groups.create_groups_get'))
    file = request.files.get('file')
    if file.filename == '':
        flash('No selected file')
        logger.debug("No selected file")
        return redirect(url_for('create_groups.create_groups_get'))
    if file and allowed_file(file.filename):
        file.seek(0)
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file.read()))
        elif file.filename.endswith(".xlsx") or file.filename.endswith(".xls"):
            df = pd.read_excel(file.read())
        else:
            flash("File type not supported")
            return redirect(url_for('create_groups.create_groups_get'))

        if current_user.get_id() is not None:
            if type(moodle_json := session.get("moodle", None)) is dict:
                current_user.moodle = MoodleSyncTesting.from_json(moodle_json)
            current_user.moodle.students = df
            session["moodle"] = current_user.moodle.to_json()

        return redirect(url_for('create_groups.create_groups_get'))
