import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = '~t\x86\xc9\x1ew\x8bOcX\x85O\xb6\xa2\x11kL\xd1\xce\x7f\x14<y\x9e'
    DEBUG = False
    LOG_DIR= "/var/log/"
    GOOGLE_ANALYTICS_TRACKING_ID = 'UA-101246577-1'
    APPLICATION_DOMAIN_NAME = "zer0point8.space"
    APPLICATION_NAME = "Training"


class DevelopmentConfig(Config):
    DEBUG = True
    #Debug toolbar stuff
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'thermos.db')
    HOST = "0.0.0.0"

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False
    SERVER_NAME = "localhost"


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'thermos.db')


config_by_name = dict(
    dev = DevelopmentConfig,
    test = TestingConfig,
    prod = ProductionConfig
)