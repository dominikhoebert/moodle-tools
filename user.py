from models import db
from moodle_sync_testing import MoodleSyncTesting


class User(db.Model):
    __tablename__ = 'user'

    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)
    moodle_url = db.Column(db.String, default="https://elearning.tgm.ac.at")
    moodle_service = db.Column(db.String, default="tgm_hoedmoodlesync")
    moodle = None

    def login(self):
        self.moodle = MoodleSyncTesting(self.moodle_url, self.username, self.password, self.moodle_service, None, None,
                                        None, None)
        self.moodle.login()
        print("Moodle login success")

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.username

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
