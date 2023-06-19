from os import getenv

from flask_sqlalchemy import SQLAlchemy
from loguru import logger
from flask_login import LoginManager
from flask_session import Session

db = SQLAlchemy()
login_manager = LoginManager()
logger.add("logs/main.log", rotation="50 MB", level="INFO")
logger.add("logs/debug.log", rotation="50 MB", level="DEBUG")
sess = Session()


class environ():
    def __init__(self):
        self.debug = bool(getenv("DEBUG", False))
        self.host = getenv("HOST", "0.0.0.0")
        self.default_moodle_url = getenv("DEFAULT_MOODLE_URL", "")
        self.default_moodle_service = getenv("DEFAULT_MOODLE_SERVICE", "")

        self.db_user = getenv("DB_USER", None)
        self.db_password = getenv("DB_PASSWORD", None)
        self.db_host = getenv("DB_HOST", "localhost")
        self.db_port = getenv("DB_PORT", "3306")

        if self.db_user is not None and self.db_password is not None:
            self.db_uri = f"mysql+mysqlconnector://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/moodle_tools"
        else:
            self.db_uri = "sqlite:///db.sqlite"


env = environ()
