import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    ORDERS_CSV = os.path.join(basedir, '../data/orders.csv')
    MODEL_PATH = os.path.join(basedir, '../data/model.dill')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DATABASE_URL = os.getenv('DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class DevelopmentConfig(Config):
    DATABASE_URL = 'sqlite:///' + os.path.join(basedir, 'arasel.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'arasel.db')


config = {
    'prod': ProductionConfig,
    'dev': DevelopmentConfig
}
