import os
from datetime import timedelta
base_dir = os.path.abspath(os.path.dirname(__file__))

class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevConfig(Config):
    DEBUG = True
    SQLITE_DB_DIR = os.path.join(base_dir, "../database")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "QuizMasterDB.sqlite3")
    SECRET_KEY = "6wd#iuh*98jdjlh12"
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT = "q_master8979salt068"
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_UNAUTHORIZED_VIEW = None
    SECURITY_URL_PREFIX = "/auth"  
    SECURITY_BLUEPRINT_NAME = "security"
    SECURITY_LOGIN_URL = None
    SECURITY_REGISTER_URL = None
    SECURITY_LOGIN_USER_TEMPLATE = "security/login.html"
    SECURITY_REGISTER_USER_TEMPLATE = "security/register.html"
    SECURITY_POST_LOGIN_VIEW = "check_roles"
    REMEMBER_COOKIE_DURATION = timedelta(days=30)