import moodle_api
import pandas as pd
import requests
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

"""
[SSL: CERTIFICATE_VERIFY_FAILED] Error: https://stackoverflow.com/questions/51925384/unable-to-get-local-issuer-certificate-when-using-requests-in-python
Install certifi; copy cacert.pem aus certifi folder
"""


class MoodleSync:
    def __init__(self, url: str, username: str, password: str, service: str):
        self.url = url
        self.key = self.get_token(username, password, service)

    def get_token(self, username, password, service):
        obj = {"username": username, "password": password, "service": service}
        response = requests.post(self.url + "/login/token.php", data=obj)
        response = response.json()
        return response['token']

    def create_group(self, groups: list):
        """ Creates a group in moodle with the given name and adds the given students to it. """
        response = moodle_api.call('core_group_create_groups', self.url, self.key, groups=groups)
        return response

    def add_students_to_group(self, members: list):
        """ Adds the given students to the given group. """
        response = moodle_api.call('core_group_add_group_members', self.url, self.key, members=members)
        return response

    def get_recent_courses(self):
        response = moodle_api.call('core_course_get_recent_courses', self.url, self.key)
        return {c['id']: c['fullname'] for c in response}

    def get_course_modules(self, course_id):
        response = moodle_api.call('core_course_get_contents', self.url, self.key, courseid=course_id)
        modules = {}
        for section in response:
            for module in section['modules']:
                if 'modname' in module:
                    if module['modname'] == 'assign':
                        modules[module['name']] = {'id': module['id']}
        return modules

    def get_gradereport_of_course(self, course_id):
        response = moodle_api.call('gradereport_user_get_grade_items', self.url, self.key, courseid=course_id)
        graditems = {}
        for graditem in response['usergrades'][0]['gradeitems']:
            graditems[graditem['itemname']] = graditem['id']

        df = pd.DataFrame(columns=['userfullname', 'userid'] + list(graditems.keys()))

        for student in response['usergrades']:
            grades = {'userfullname': student['userfullname'], "userid": student['userid']}
            for gradeitem in student['gradeitems']:
                grades[gradeitem['itemname']] = gradeitem['gradeformatted']
            df = df.append(grades, ignore_index=True)

        df = df.rename(columns={None: 'Kurs', 'userfullname': 'Schüler'})
        return df

    def get_enrolled_students(self, course_id):
        """
        Returns a DataFrame with user info id, fullname, email, groups (all groups as joined str)"""
        response = moodle_api.call('core_enrol_get_enrolled_users', self.url, self.key, courseid=course_id)
        new_rows = []
        for student in response:
            new_rows.append([student["id"], student["firstname"], student["lastname"], student["email"]])

        user_df = pd.DataFrame(new_rows, columns=['id_joined', 'firstname', 'lastname', 'email_joined'])
        return user_df

    def get_student_info(self, userlist):
        """
        Takes an array of dict with key userid=int, courseid=int
        Returns a DataFrame with user info id, fullname, email, groups (all groups as joined str)

        :param userlist:
        :return DataFrame:
        """
        response = moodle_api.call('core_user_get_course_user_profiles', self.url, self.key, userlist=userlist)
        user_df = pd.DataFrame(columns=['id', 'fullname', 'email', 'groups'])
        for student in response:
            groups_list = []
            for group in student["groups"]:
                groups_list.append(group["name"])
            groups = ""
            if len(groups_list) > 0:
                groups = ",".join(groups_list)
            user_df = user_df.append(
                {"id": student["id"], "fullname": student["fullname"], "email": student["email"], "groups": groups},
                ignore_index=True)

        return user_df

    def enroll_students(self, enrolments: list):
        """ Enrolls the given students in the given course. """
        r = moodle_api.call('enrol_manual_enrol_users', self.url, self.key, enrolments=enrolments)
        return r

    def get_user_by_email(self, emails: list):
        response = moodle_api.call('core_user_get_users_by_field', self.url, self.key, field="email", values=emails)
        return response


if __name__ == "__main__":
    import json

    with open("../Moodle_Sync_Testing_Textual/data/credentials.json", "r") as f:
        credentials = json.load(f)
    url = credentials["url"]
    username = credentials["user"]
    password = credentials["password"]
    service = credentials["service"]
    ms = MoodleSync(url, username, password, service)
    print(ms.get_user_by_email(["dhoebert@tgm.ac.at"]))
