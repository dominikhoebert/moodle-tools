from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import current_user
import pandas as pd
import io

from moodle_sync_testing import MoodleSyncTesting

from models import logger

create_groups = Blueprint("create_groups", __name__, url_prefix="/create-groups")

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

toast_html = open("templates/toast.html", "r").read()
course_links_html = open("templates/course_links.html", "r").read()


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
    if current_user.get_id() is not None:
        return render_template("create_groups.html", username=current_user.get_id())
    return redirect(url_for("reporting.login"))


def ajax_flash(message: str, response: dict = None):
    if response is None:
        response = dict()
    response['flash'] = toast_html.replace("{{message}}", message)
    return response


def buttons_html(button: str, activated: bool = False, response: dict = None):
    if response is None:
        response = dict()
    if button == "enroll" or button == 'all':
        if activated:
            response['enroll-button'] = '<a class="btn btn-secondary" onclick="update(\'enroll\')" ' \
                                        'role="button">Enroll missing students</a>'
        else:
            response['enroll-button'] = '<a class="btn btn-secondary disabled" role="button" ' \
                                        'aria-disabled="true">Enroll missing students</a>'
    if button == "create" or button == 'all':
        if activated:
            response['create-button'] = '<a class="btn btn-secondary" onclick="update(\'create\')" ' \
                                        'role="button">Create Groups</a>'
        else:
            response['create-button'] = '<a class="btn btn-secondary disabled" role="button" ' \
                                        'aria-disabled="true">Create Groups</a>'
    if button == "add" or button == 'all':
        if activated:
            response['add-button'] = '<a class="btn btn-secondary" onclick="update(\'add\')" ' \
                                     'role="button">Add students to groups</a>'
        else:
            response['add-button'] = '<a class="btn btn-secondary disabled" role="button" ' \
                                     'aria-disabled="true">Add students to groups</a>'
    return response


def create_response(kind: str, moodle: MoodleSyncTesting, response: dict = None):
    if response is None:
        response = dict()
    if moodle.course_id is not None and (kind == "course" or kind == "all"):
        response['select-course-id'] = moodle.courses[moodle.course_id]
        response['course-links'] = course_links_html.replace("{{id}}", str(moodle.course_id)).replace("{{url}}",
                                                                                                      moodle.url)
        if moodle.groups is not None:
            if len(moodle.groups) > 0:
                groups = '<div class="list-group">'
                for group in moodle.groups:
                    groups += '<a target="_blank" rel="noopener noreferrer" href="' + moodle.url + \
                              '/group/members.php?group=' + str(group['id'])
                    groups += '" class="list-group-item list-group-item-action">' + group["name"] + '</a>'
                response['current-groups-preview'] = groups + '</div>'
            else:
                response['current-groups-preview'] = "No existing groups"
    if moodle.courses is not None and (kind == "course_list" or kind == "all"):
        courses_html = ""
        for course_id, course_name in moodle.courses.items():
            courses_html += f'<li><a class="dropdown-item" onclick="update(\'course/\' + {course_id})">{course_name}</a></li>'
        response['select-course-list'] = courses_html
    if moodle.students is not None and (kind == "student_list" or kind == "all"):
        response['student-preview'] = moodle.students_original.to_html(table_id="datatablesSimple")
        group_column_names_html = ""
        column_names_html = ""
        for column_names in moodle.students_original.columns.to_list():
            group_column_names_html += '<li><a class="dropdown-item" onclick="update(\'groupname/' + column_names \
                                       + '\')">' + column_names + '</a></li>'
            column_names_html += '<li><a class="dropdown-item" onclick="update(\'column/' + column_names + '\')">' \
                                 + column_names + '</a></li>'
        response['select-group-list'] = group_column_names_html
        response['column-name-list'] = column_names_html
    if moodle.group_column_name is not None and (kind == "group_name" or kind == "all"):
        response['select-group'] = moodle.group_column_name
        new_groups = moodle.count_students_in_groups()
        new_groups = pd.DataFrame(new_groups).reset_index().rename(columns={'name': 'Students'}).to_html(
            classes="table table-striped table-hover", justify="left")
        response['groups-preview'] = new_groups
        if moodle.course_id is not None and moodle.right_on is not None:
            response = buttons_html("create", True, response)
    if moodle.right_on is not None and (kind == "column_name" or kind == "all"):
        response['column-name'] = moodle.column_name
        if moodle.course_id is not None:
            response = buttons_html("enroll", True, response)
    if moodle.group_names_to_id is not None and kind == "all":
        response = buttons_html("add", True, response)
    return response


def check_all_groups_exist(moodle: MoodleSyncTesting):
    if moodle.groups is None or moodle.students is None or moodle.group_column_name is None:
        return False
    existing_groups = [g["name"] for g in moodle.groups]
    for group in moodle.group_names():
        if group not in existing_groups:
            return False
    return True


@create_groups.route("/get_all")
def get_all():
    if current_user.get_id() is not None:
        if get_moodle() is not None:
            return create_response(kind="all", moodle=current_user.moodle)
    return redirect(url_for("reporting.login"))  # TODO error message?


@create_groups.post("/file-upload")
def file_upload():
    if 'file' not in request.files:
        return ajax_flash("No file part")
    file = request.files.get('file')
    if file.filename == '':
        return ajax_flash("No selected file")
    if file and allowed_file(file.filename):
        file.seek(0)
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file.read()))
        elif file.filename.endswith(".xlsx") or file.filename.endswith(".xls"):
            df = pd.read_excel(file.read())
        else:
            return ajax_flash("File type not supported")

        if get_moodle() is not None:
            current_user.moodle.students_original = None
            current_user.moodle.students = df
            current_user.moodle.column_name = None  # reset column names
            current_user.moodle.group_column_name = None  # reset group column names
            current_user.moodle.group_names_to_id = None  # reset group names
            session["moodle"] = current_user.moodle.to_json()

            response = create_response(kind='student_list', moodle=current_user.moodle)
            response = create_response(kind='group_name', moodle=current_user.moodle, response=response)
            response['select-group'] = "Select"
            response['column-name'] = "Select"
            response = buttons_html(button='all', activated=False, response=response)
            response['groups-preview'] = ""

            return response
    return ajax_flash("File type not supported")


@create_groups.route("/course/<int:course_id>")
def course(course_id):
    if course_id is not None and course_id != 0:
        if get_moodle() is not None:
            moodle = current_user.moodle
            moodle.course_id = course_id
            moodle.group_names_to_id = None  # reset group names
            moodle.groups = moodle.get_groups(moodle.course_id)
            session["moodle"] = moodle.to_json()

            response = create_response(kind="course", moodle=moodle)
            response = buttons_html(button='add', activated=check_all_groups_exist(moodle), response=response)
            if moodle.course_id is not None and moodle.right_on is not None:
                response = buttons_html(button='enroll', activated=True, response=response)
            if moodle.group_column_name is not None and moodle.right_on is not None:
                response = buttons_html(button='create', activated=True, response=response)
            return response
    return {"Error", "while selecting course"}


@create_groups.route("/column/<column_name>")
def column(column_name):
    if column_name is not None and column_name != "":
        if get_moodle() is not None:
            moodle = current_user.moodle
            moodle.column_name = column_name
            moodle.group_names_to_id = None  # reset group names
            session["moodle"] = moodle.to_json()

            response = create_response(kind="column_name", moodle=moodle)
            response = buttons_html(button='add', activated=check_all_groups_exist(moodle), response=response)
            if moodle.right_on is None:
                response = ajax_flash("Error: Email/Moodle-ID could not be recognised! Please choose a different one.")
            elif moodle.course_id is not None:
                response = buttons_html(button='enroll', activated=True, response=response)
                if moodle.group_column_name is not None:
                    response = buttons_html(button='create', activated=True, response=response)
            return response
    return {"Error", "while selecting course"}


@create_groups.route("/groupname/<group_column_name>")
def groupname(group_column_name):
    if group_column_name is not None and group_column_name != "":
        if get_moodle() is not None:
            moodle = current_user.moodle
            moodle.group_column_name = group_column_name
            moodle.group_names_to_id = None  # reset group names
            session["moodle"] = moodle.to_json()

            response = create_response(kind="group_name", moodle=moodle)
            response = buttons_html(button='add', activated=check_all_groups_exist(moodle), response=response)
            if moodle.course_id is not None and moodle.right_on is not None:
                response = buttons_html(button='create', activated=True, response=response)
            return response
    return {"Error", "while selecting course"}


@create_groups.route("/enroll")
def enroll():
    if get_moodle() is not None:
        moodle = current_user.moodle
        moodle.join_enrolled_students()
        not_enrolled = moodle.get_not_enrolled_students()
        moodle.enroll_students_for_groups()
        session["moodle"] = moodle.to_json()
        return ajax_flash(f"{len(not_enrolled)} Students enrolled")
    return redirect(url_for('create_groups.create_groups_get'))


@create_groups.route("/create")
def create():
    if get_moodle() is not None:
        moodle = current_user.moodle
        moodle.join_enrolled_students()
        moodle.clean_students()
        groups_count = moodle.create_groups()
        moodle.groups = moodle.get_groups(moodle.course_id)
        session["moodle"] = moodle.to_json()

        response = ajax_flash(f"{groups_count} Groups created")
        response = create_response(kind="course", moodle=moodle)
        if moodle.group_names_to_id is not None:
            response = buttons_html(button='add', activated=True, response=response)
        return response
    return redirect(url_for('create_groups.create_groups_get'))


@create_groups.route("/add")
def add():
    if get_moodle() is not None:
        moodle = current_user.moodle
        moodle.add_students_to_groups()
        session["moodle"] = moodle.to_json()
        return ajax_flash("Students added to groups")
    return redirect(url_for('create_groups.create_groups_get'))
