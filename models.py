from flask_sqlalchemy import SQLAlchemy
from loguru import logger
from flask_login import LoginManager
from flask_session import Session

db = SQLAlchemy()
login_manager = LoginManager()
logger.add("logs/main.log", rotation="50 MB", level="INFO")
logger.add("logs/debug.log", rotation="50 MB", level="DEBUG")
sess = Session()
