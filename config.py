import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('WTL_SECRET_KEY')
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SENDER = os.environ.get('MAIL_SENDER')
    MAIL_SUBJECT_PREFIX = "[WTL]"
    ADMIN_WTL = os.environ.get('MAIL_SENDER')


class ConfigDev(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('WTL_DATABASE_URL_DEV')


config = {
    "dev": ConfigDev,
}