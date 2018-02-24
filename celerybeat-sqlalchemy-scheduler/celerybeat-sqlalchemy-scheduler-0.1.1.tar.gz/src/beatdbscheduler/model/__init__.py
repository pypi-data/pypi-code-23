from celery import current_app
from sqlalchemy import event
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import MetaData

from .base import Base
from .model import (
    CrontabSchedule, PeriodicTask, PeriodicTasks, IntervalSchedule
)

__all__ = [
    'Base', 'CrontabSchedule', 'PeriodicTask', 'PeriodicTasks',
    'IntervalSchedule'
]

engine = create_engine(
    current_app.conf.ENGINE_URL, pool_size=20, pool_recycle=3600
)
Session = sessionmaker(bind=engine, autocommit=True)
metadata = MetaData(bind=engine)


def get_session():
    return Session()


@event.listens_for(Session, 'before_flush')
def before_flush(session, flush_context, instances):
    for obj in session.new | session.dirty:
        if isinstance(obj, PeriodicTask):
            if not obj.interval and not obj.crontab:
                raise ValueError(
                    'One of interval or crontab must be set.'
                )
            if obj.interval and obj.crontab:
                raise ValueError(
                    'Only one of interval or crontab must be set'
                )
            PeriodicTasks.changed(session, obj)
