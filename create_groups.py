from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import current_user
from markupsafe import Markup
import pandas as pd
import io

from moodle_sync_testing import MoodleSyncTesting

from models import logger

create_groups = Blueprint("create_groups", __name__, url_prefix="/create-groups")

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_moodle():
    if current_user.get_id() is not None:
        if type(moodle_json := session.get("moodle", None)) is dict:
            current_user.moodle = MoodleSyncTesting.from_json(moodle_json)
            return current_user.moodle
    return None


@create_groups.get("/")
def create_groups_get():
    students = None
    columns = None
    course_name = None
    if current_user.get_id() is not None:
        if get_moodle() is not None:
            if current_user.moodle.students is not None:
                students = current_user.moodle.students.to_html(table_id="datatablesSimple")
                columns = current_user.moodle.students.columns.to_list()
            if current_user.moodle.course_id is not None:
                course_name = current_user.moodle.courses[current_user.moodle.course_id]
                if current_user.moodle.group_column_name is not None:
                    # color students preview column
                    # create groups preview
                    ...
                if current_user.moodle.column_name is not None:
                    # color students preview column
                    # activate enroll missing students button
                    # color students preview missing students rows
                    ...
                if current_user.moodle.group_column_name is not None and current_user.moodle.column_name is not None:
                    # activate create groups button
                    ...
                if current_user.moodle.group_names_to_id is not None:
                    # activate create add students to groups button
                    ...
        return render_template("create_groups.html", username=current_user.get_id(),
                               students=students, courses=current_user.moodle.courses,
                               columns=columns, course_id=course_name,
                               group_column_name=current_user.moodle.group_column_name,
                               column_name=current_user.moodle.column_name)
    return redirect(url_for("reporting.login"))


@create_groups.post("/file-upload")
def file_upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('create_groups.create_groups_get'))
    file = request.files.get('file')
    if file.filename == '':
        flash('No selected file')
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

        if get_moodle() is not None:
            current_user.moodle.students = df
            session["moodle"] = current_user.moodle.to_json()

        return redirect(url_for('create_groups.create_groups_get'))


@create_groups.route("/course/<int:course_id>")
def course(course_id):
    if course_id is not None and course_id != 0:
        if get_moodle() is not None:
            current_user.moodle.course_id = course_id
            session["moodle"] = current_user.moodle.to_json()
    return redirect(url_for('create_groups.create_groups_get'))


@create_groups.route("/column/<column_name>")
def column(column_name):
    if column_name is not None and column_name != "":
        if get_moodle() is not None:
            logger.debug("success")
            current_user.moodle.column_name = column_name
            session["moodle"] = current_user.moodle.to_json()
    return redirect(url_for('create_groups.create_groups_get'))


@create_groups.route("/groupname/<group_column_name>")
def groupname(group_column_name):
    if group_column_name is not None and group_column_name != "":
        if get_moodle() is not None:
            current_user.moodle.group_column_name = group_column_name
            session["moodle"] = current_user.moodle.to_json()
    return redirect(url_for('create_groups.create_groups_get'))


@create_groups.route("/enroll")
def enroll():
    if get_moodle() is not None:
        current_user.moodle.join_enrolled_students()
        current_user.moodle.enroll_students_for_groups()
        session["moodle"] = current_user.moodle.to_json()
        flash("xxx Students enrolled")  # TODO: add number of students
    return redirect(url_for('create_groups.create_groups_get'))


@create_groups.route("/create")
def create():
    if get_moodle() is not None:
        current_user.moodle.join_enrolled_students()
        current_user.moodle.clean_students()
        current_user.moodle.create_groups()
        session["moodle"] = current_user.moodle.to_json()
        flash("xxx Groups created")  # TODO: add number of groups
    return redirect(url_for('create_groups.create_groups_get'))


@create_groups.route("/add")
def add():
    if get_moodle() is not None:
        current_user.moodle.add_students_to_groups()
        session["moodle"] = current_user.moodle.to_json()
        flash("xxx Students added to xxx groups")  # TODO: add number of students
    return redirect(url_for('create_groups.create_groups_get'))
