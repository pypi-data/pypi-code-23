from flask_sqlalchemy import SQLAlchemy
from .constants import *
from .utils import *
import datetime
from app import db


def get_session():
    return db.create_scoped_session(options={'autocommit': True, 'autoflush': False})


class Sequence(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    key = db.Column(db.String(50), unique=True)
    value = db.Column(db.Integer, nullable=True)
    template = db.Column(db.String(50), nullable=True)
    created_time = db.Column(db.DateTime, nullable=True)
    update_time = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<Sequence {}>'.format(self.key)

    def increment(self, commit=True):
        # sequence_session = get_session()
        self.value += 1
        self.update_time = datetime.datetime.now()
        if commit:
            db.session.flush()

    def next_value(self, template=None, params=None,
                   expanders=None, commit=True):

        default_template = self.template

        default_expanders = SEQUENCE_FIELD_DEFAULT_EXPANDERS

        count = self.value
        template = template if template is not None else default_template
        params = params if params is not None else {}
        expanders = expanders if expanders is not None else default_expanders
        if commit:
            self.increment()
        return expand(template, count, params, expanders=expanders)

    @classmethod
    def create_if_missing(cls, key, template=None):
        default_template = SEQUENCE_FIELD_DEFAULT_TEMPLATE
        try:
            # sequence_session=get_session()
            seq = db.session.query(cls).filter_by(key=key).first()
            if seq:
                return seq
            else:
                seq = Sequence()
                seq.value=SEQUENCE_DEFAULT_VALUE
                seq.key = key
                seq.template = template or default_template
                seq.created_time = datetime.datetime.now()
                db.session.add(seq)
                db.session.commit()
                return seq
        except Exception:
            return None

    @classmethod
    def next(cls, key, template=None, params=None,
             expanders=None, commit=True):
        seq = Sequence.create_if_missing(key, template)
        return seq.next_value(template, params, expanders, commit)

    @classmethod
    def get_template_by_key(cls, key):
        default_template = SEQUENCE_FIELD_DEFAULT_TEMPLATE
        try:
            db_session=get_session()
            seq = db_session.query(Sequence).filter_by(key=key).first()
            return seq.template
        except Exception:
            return default_template
