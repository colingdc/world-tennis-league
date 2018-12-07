import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True


class ConfigDev(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('WTL_DATABASE_URL_DEV')


config = {
    "dev": ConfigDev,
}