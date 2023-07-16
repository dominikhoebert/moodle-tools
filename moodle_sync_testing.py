import pandas as pd
from pandas import DataFrame
from datetime import datetime
import random
import json

from moodle_sync import MoodleSync
from models import logger


class MoodleSyncTesting(MoodleSync):
    def __init__(self, url: str, username: str, service: str, course_id: int, students: DataFrame,
                 column_name: str, group_column_name: str, students_original: DataFrame = None):
        self.url = url
        self.username = username
        self.service = service
        self.course_id = course_id
        self._students = None
        self.students_original = students_original
        self.students = students
        self.right_on = None
        self.column_name = column_name
        self.group_column_name = group_column_name
        self.group_names_to_id = None
        self.courses = None
        self.groups = None

    def login(self, password):
        super().__init__(self.url, self.username, password, self.service)

    def __repr__(self):
        return f"MoodleSyncTesting(url={self.url}, username={self.username}, service=" \
               f"{self.service}, course_id={self.course_id}, students={self.students}, column_name={self.column_name}" \
               f", group_column_name={self.group_column_name})"

    def to_json(self):
        return {
            "url": self.url,
            "username": self.username,
            "service": self.service,
            "course_id": self.course_id,
            "students_original": self.students_original.to_json() if self.students_original is not None else None,
            "students": self.students.to_json() if self.students is not None else None,
            "column_name": self.column_name,
            "group_column_name": self.group_column_name,
            "group_names_to_id": self.group_names_to_id,
            "courses": self.courses if self.courses is not None else None,
            "token": self.key,
            "groups": json.dumps(self.groups) if self.groups is not None else None,
        }

    def from_json(moodle_json):
        mst = MoodleSyncTesting(moodle_json["url"], moodle_json["username"], moodle_json["service"],
                                moodle_json["course_id"],
                                pd.read_json(moodle_json["students"]) if moodle_json["students"] is not None else None,
                                moodle_json["column_name"], moodle_json["group_column_name"],
                                students_original=pd.read_json(moodle_json["students_original"]) if moodle_json[
                                                                                                        "students_original"] is not None else None)
        mst.group_names_to_id = moodle_json["group_names_to_id"]
        mst.courses = moodle_json["courses"]
        mst.key = moodle_json["token"]
        mst.url = moodle_json["url"]
        mst.groups = json.loads(moodle_json["groups"]) if moodle_json["groups"] is not None else None
        return mst

    @property
    def students(self):
        return self._students

    @students.setter
    def students(self, value: DataFrame):
        if self.students_original is None:
            self.students_original = value
        self._students = value

    @property
    def column_name(self):
        return self._column_name

    @column_name.setter
    def column_name(self, value: str):
        self._column_name = value
        self.right_on = self.get_right_on()

    def get_right_on(self):
        if self.column_name is not None:
            if self.is_id_column():
                # logger.debug("Column Name detected as ID")
                return "id_joined"
            elif self.is_email_column():
                # logger.debug("Column Name detected as Email")
                return "email_joined"
            else:
                # logger.debug("Column Name could not be detected as ID or Email")
                return None

    def join_enrolled_students(self):
        enrolled_students_df = self.get_enrolled_students(self.course_id)
        self.students = self.students_original.merge(enrolled_students_df, left_on=self.column_name,
                                                     right_on=self.right_on, how="left")

    def is_email_column(self) -> bool:
        return self.column_name in self.students.columns and self.students[self.column_name].str.contains("@").any()

    def is_id_column(self) -> bool:
        return self.column_name in self.students.columns and self.students[self.column_name].dtype == "int64"

    def clean_students(self):
        self.students = self.students[self.students["id_joined"].notnull()]
        self.students = self.students[self.students[self.group_column_name].notnull()]
        self.students = self.students[self.students[self.group_column_name] != ""]

    def group_names(self):
        return self.students[self.group_column_name].unique()

    def create_groups(self):
        groups = []
        group_ids = {}
        date_string = datetime.now().strftime("%Y%m%d")
        self.group_names_to_id = {}
        already_existing_groups = {group["name"]: group["id"] for group in self.groups if self.groups is not None}
        for g in self.group_names():
            if g in already_existing_groups:
                self.group_names_to_id[g] = already_existing_groups[g]
            else:
                group_id = date_string + str(random.randrange(100, 999))
                group_ids[g] = group_id
                groups.append(
                    {"courseid": self.course_id, "name": g, "description": "", "idnumber": group_id})
        if len(groups) > 0:
            response = self.create_group(groups)
            for g in response:
                self.group_names_to_id[g["name"]] = g["id"]
        return len(groups)

    def log_groups(self):
        logger.debug("Groups created:")
        for g, id in self.group_names_to_id.items():
            logger.debug(f"{g} ({id})")

    def add_students_to_groups(self):
        members = []
        logger.debug("Adding students to groups:")
        for group_name, group_id in self.group_names_to_id.items():
            for index, row in self.students[self.students[self.group_column_name] == group_name].iterrows():
                logger.debug(f"{row[self.column_name]} ({row['id_joined']}) to {group_name} ({group_id})")
                members.append({"groupid": group_id, "userid": int(row["id_joined"])})

        self.add_students_to_group(members)

    def count_students_in_groups(self):
        grouped = self.students.groupby(self.group_column_name).count()
        return grouped[grouped.columns[0]]

    def log_count_students_in_groups(self):
        logger.debug("Students in groups:")
        logger.debug(self.count_students_in_groups())

    def get_not_enrolled_students(self):
        return self.students[self.students["id_joined"].isnull()]

    def enroll_students_for_groups(self):
        not_enrolled_df = self.get_not_enrolled_students()
        if len(not_enrolled_df) > 0:
            if self.right_on == 'id_joined':
                not_enrolled_ids = not_enrolled_df[self.column_name].tolist()
                logger.debug(f"Enrolling {len(not_enrolled_ids)} students")
                logger.debug(f"IDs: {not_enrolled_ids}")
            elif self.right_on == 'email_joined':
                emails = not_enrolled_df[self.column_name].tolist()
                response = self.get_user_by_email(emails)
                not_enrolled_ids = [s["id"] for s in response]
                logger.debug(f"Enrolling {len(not_enrolled_ids)} students")
                logger.debug(f"Emails: {emails}")
                logger.debug(f"IDs: {not_enrolled_ids}")
            else:
                return
            enrolments = []
            for id in not_enrolled_ids:
                enrolments.append({'roleid': 5, 'userid': id, 'courseid': self.course_id})  # 5 = student
            self.enroll_students(enrolments)

    def get_missing_students(self):
        if self.right_on is not None and self.course_id is not None:
            self.join_enrolled_students()
            missing_students = self.get_not_enrolled_students()
            missing_students = missing_students[self.column_name].tolist()
            return missing_students
        else:
            return None

    def check_all_groups_exist(self):
        if self.groups is None or self.students is None or self.group_column_name is None:
            return False
        existing_groups = [g["name"] for g in self.groups]
        for group in self.group_names():
            if group not in existing_groups:
                return False
        return True

    def add_existing_groups(self):
        if self.check_all_groups_exist():
            self.group_names_to_id = {group["name"]: group["id"] for group in self.groups}


if __name__ == '__main__':
    import json

    with open("data/credentials.json", "r") as f:
        credentials = json.load(f)

    moodle_sync = MoodleSyncTesting(credentials["url"], credentials["user"],
                                    credentials["service"], course_id=1309, students=pd.read_csv("data/test.csv"),
                                    column_name="email", group_column_name="groupname")

    # print(moodle_sync.count_students_in_groups())
    moodle_sync.login(credentials["password"])
    print(moodle_sync.get_groups(1309))
    # moodle_sync.log_count_students_in_groups()
    # print(moodle_sync)
    # json = moodle_sync.to_json()
    # print(json)
    # new_moodle_sync = MoodleSyncTesting.from_json(json)
    # new_moodle_sync.login()
    # new_moodle_sync.log_count_students_in_groups()
    # print(new_moodle_sync)

    # moodle_sync.join_enrolled_students()
    # moodle_sync.enroll_students_for_groups()
    # moodle_sync.join_enrolled_students()
    # moodle_sync.clean_students()
    # moodle_sync.create_groups()
    # moodle_sync.log_groups()
    # moodle_sync.add_students_to_groups()
