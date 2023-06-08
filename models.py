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


env = environ()
