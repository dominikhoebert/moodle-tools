from models import db
from moodle_sync_testing import MoodleSyncTesting


class User(db.Model):
    __tablename__ = 'user'

    username = db.Column(db.String, primary_key=True)
    authenticated = db.Column(db.Boolean, default=False)
    moodle_url = None
    moodle_service = None
    moodle = None

    def login(self, password):
        self.moodle = MoodleSyncTesting(self.moodle_url, self.username, self.moodle_service, None, None,
                                        None, None)
        self.moodle.login(password)
        self.moodle.courses = self.moodle.get_recent_courses()

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
