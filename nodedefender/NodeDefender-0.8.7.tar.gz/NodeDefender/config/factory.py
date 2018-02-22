import NodeDefender

class DefaultConfig:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "key"
    SECRET_SALT = "salt"
    PORT = 5000
    SELF_REGISTRATION = True
    WTF_CSRF_ENABLED = False

    DATABASE = False
    REDIS = False
    LOGGING = False
    MAIL = False
    CELERY = False

class TestingConfig(DefaultConfig):
    TESTING = True
    DATABASE = False
    LOGGING = False
    MAIL = False
    CELERY = False
