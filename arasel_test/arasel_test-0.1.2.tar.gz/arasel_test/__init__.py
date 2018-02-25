
"""Top-level package for Arasel Python Test."""
import numpy
import dill

__author__ = """Alberto Egido"""
__version__ = '0.1.2'

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()

from arasel_test.config import config
from arasel_test.arasel_etl import AraselETL
from arasel_test.models import Customer


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    with app.app_context():
        db.create_all()


    return app


def load_db(app, db):
    with app.app_context():
        with open(app.config['MODEL_PATH'], 'rb') as f:
            model = dill.dill.load(f)

        etl = AraselETL(app.config['ORDERS_CSV'], model)
        customer_clvs = etl.customer_clvs

        for customer_id, clv in customer_clvs.items():
            customer = Customer(customer_id=customer_id, clv=clv)
            db.session.merge(customer)

        db.session.commit()
