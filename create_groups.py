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


def color_html_table(html: str, find_str: str, tag: str):
    pos = html.find(find_str)
    html = html[:pos] + tag + html[pos:]
    return html


@create_groups.get("/")
def create_groups_get():
    students = None
    columns = None
    course_name = None
    groups = None
    if current_user.get_id() is not None:
        if get_moodle() is not None:
            if current_user.moodle.students is not None:
                students = current_user.moodle.students_original.to_html(table_id="datatablesSimple")
                columns = current_user.moodle.students_original.columns.to_list()
            if current_user.moodle.course_id is not None:
                course_name = current_user.moodle.courses[current_user.moodle.course_id]
                if current_user.moodle.group_column_name is not None:
                    # color students preview column
                    students = color_html_table(students, ">" + current_user.moodle.group_column_name,
                                                ' class="table-warning"')
                    # create groups preview
                    groups = current_user.moodle.count_students_in_groups()  # TODO error when wrong column name
                    groups = pd.DataFrame(groups).reset_index().rename(columns={'name': 'Students'}).to_html(
                        classes="table table-striped table-hover", justify="left")
                if current_user.moodle.column_name is not None:
                    # TODO color students preview column
                    # TODO color students preview missing students rows
                    ...
        return render_template("create_groups.html", username=current_user.get_id(),
                               students=students, courses=None,
                               columns=columns, course_id=None,
                               group_column_name=None,
                               column_name=None, groups_preview=groups,
                               group_names=current_user.moodle.group_names_to_id)
    return redirect(url_for("reporting.login"))


def create_response(moodle: MoodleSyncTesting):
    response = dict()
    if moodle.course_id is not None:
        response['course_name'] = moodle.courses[current_user.moodle.course_id]
    if moodle.courses is not None:
        courses_html = ""
        for course_id, course_name in moodle.courses.items():
            courses_html += f'<li><a class="dropdown-item" onclick="course({course_id})">{course_name}</a></li>'
        response['courses'] = courses_html
    if moodle.students is not None:
        response['students'] = moodle.students.to_html(table_id="datatablesSimple")  # TODO to html?
        response['columns'] = moodle.students.columns.to_list()  # TODO to html
    if moodle.group_column_name is not None:
        response['group_column_name'] = moodle.group_column_name
    if moodle.column_name is not None:
        response['column_name'] = moodle.column_name
    if moodle.group_names_to_id is not None:
        response['group_names'] = moodle.group_names_to_id

    return response


@create_groups.route("/get_all")
def get_all():
    if current_user.get_id() is not None:
        if get_moodle() is not None:
            return create_response(current_user.moodle)
    return redirect(url_for("reporting.login"))  # TODO error message?


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
            current_user.moodle.students_original = None
            current_user.moodle.students = df
            current_user.moodle.column_name = None  # reset column names
            current_user.moodle.group_column_name = None  # reset group column names
            current_user.moodle.group_names_to_id = None  # reset group names
            session["moodle"] = current_user.moodle.to_json()

        return redirect(url_for('create_groups.create_groups_get'))


@create_groups.route("/course/<int:course_id>")
def course(course_id):
    if course_id is not None and course_id != 0:
        if get_moodle() is not None:
            current_user.moodle.course_id = course_id
            current_user.moodle.group_names_to_id = None  # reset group names
            session["moodle"] = current_user.moodle.to_json()
            return create_response(current_user.moodle)
    return {"Error", "while selecting course"}
    # return redirect(url_for('create_groups.create_groups_get'))


@create_groups.route("/column/<column_name>")
def column(column_name):
    if column_name is not None and column_name != "":
        if get_moodle() is not None:
            current_user.moodle.column_name = column_name
            current_user.moodle.group_names_to_id = None  # reset group names
            session["moodle"] = current_user.moodle.to_json()
            return create_response(current_user.moodle)
    return {"Error", "while selecting course"}
    # return redirect(url_for('create_groups.create_groups_get'))


@create_groups.route("/groupname/<group_column_name>")
def groupname(group_column_name):
    if group_column_name is not None and group_column_name != "":
        if get_moodle() is not None:
            current_user.moodle.group_column_name = group_column_name
            current_user.moodle.group_names_to_id = None  # reset group names
            session["moodle"] = current_user.moodle.to_json()
            return create_response(current_user.moodle)
    return {"Error", "while selecting course"}
    # return redirect(url_for('create_groups.create_groups_get'))


@create_groups.route("/enroll")
def enroll():
    if get_moodle() is not None:
        current_user.moodle.join_enrolled_students()
        not_enrolled = current_user.moodle.get_not_enrolled_students()
        current_user.moodle.enroll_students_for_groups()
        session["moodle"] = current_user.moodle.to_json()
        flash(f"{len(not_enrolled)} Students enrolled")
    return redirect(url_for('create_groups.create_groups_get'))


@create_groups.route("/create")
def create():
    if get_moodle() is not None:
        current_user.moodle.join_enrolled_students()
        current_user.moodle.clean_students()
        current_user.moodle.create_groups()
        session["moodle"] = current_user.moodle.to_json()
        flash(f"{len(current_user.moodle.group_names_to_id)} Groups created")
    return redirect(url_for('create_groups.create_groups_get'))


@create_groups.route("/add")
def add():
    if get_moodle() is not None:
        current_user.moodle.add_students_to_groups()
        session["moodle"] = current_user.moodle.to_json()
        flash("Students added to groups")
    return redirect(url_for('create_groups.create_groups_get'))
