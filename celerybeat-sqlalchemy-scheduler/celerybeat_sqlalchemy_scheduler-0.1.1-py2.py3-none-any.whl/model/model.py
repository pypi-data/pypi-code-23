import datetime

from sqlalchemy.orm import relationship
from celery import schedules, current_app
from sqlalchemy import create_engine
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy_utils.types.choice import ChoiceType

from .base import Base

engine = create_engine(
    current_app.conf.ENGINE_URL, pool_size=20, pool_recycle=3600
)


class IntervalSchedule(Base):
    __tablename__ = "interval_schedule"
    PERIOD_CHOICES = (
        ('days', 'Days'), ('hours', 'Hours'), ('minutes', 'Minutes'),
        ('seconds', 'Seconds'), ('microseconds', 'Microseconds')
    )

    every = Column(Integer, nullable=False)
    period = Column(ChoiceType(PERIOD_CHOICES))
    periodic_tasks = relationship('PeriodicTask')

    @property
    def schedule(self):
        return schedules.schedule(
            datetime.timedelta(**{self.period.code: self.every})
        )

    @classmethod
    def from_schedule(cls, session, schedule, period='seconds'):
        every = max(schedule.run_every.total_seconds(), 0)
        obj = cls.filter_by(session, every=every, period=period).first()
        if obj is None:
            return cls(every=every, period=period)
        else:
            return obj

    def __str__(self):
        if self.every == 1:
            return 'every {0.period_singular}'.format(self)
        return 'every {0.every} {0.period}'.format(self)

    @property
    def period_singular(self):
        return self.period[:-1]

    def save(self):
        pass


class CrontabSchedule(Base):
    """Task result/status."""

    __tablename__ = 'crontab_schedule'
    minute = Column(String(length=120), default='*', index=True)
    hour = Column(String(length=120), default='*', index=True)
    day_of_week = Column(String(length=120), default='*', index=True)
    day_of_month = Column(String(length=120), default='*', index=True)
    month_of_year = Column(String(length=120), default='*', index=True)
    periodic_tasks = relationship('PeriodicTask')

    @property
    def schedule(self):
        return schedules.crontab(
            minute=self.minute,
            hour=self.hour,
            day_of_week=self.day_of_week,
            day_of_month=self.day_of_month,
            month_of_year=self.month_of_year
        )

    @classmethod
    def from_schedule(cls, session, schedule):
        spec = {
            'minute': str(schedule._orig_minute),
            'hour': str(schedule._orig_hour),
            'day_of_week': str(schedule._orig_day_of_week),
            'day_of_month': str(schedule._orig_day_of_month),
            'month_of_year': str(schedule._orig_month_of_year)
        }
        obj = cls.filter_by(session, **spec).first()
        if obj is None:
            return cls(**spec)
        else:
            return obj

    def save(self):
        pass


class PeriodicTasks(Base):
    __tablename__ = "periodic_tasks"

    ident = Column(Integer, default=1, autoincrement=True, index=True)
    last_update = Column(
        DateTime, default=datetime.datetime.utcnow, index=True
    )

    @classmethod
    def changed(cls, session, instance):
        if not instance.no_changes:
            obj, _ = cls.update_or_create(
                session,
                defaults={'last_update': datetime.datetime.now()},
                ident=1
            )
            session.add(obj)

    @classmethod
    def last_change(cls, session):
        obj = cls.filter_by(session, ident=1).first()
        return obj.last_update if obj else None

    def save(self):
        pass


class PeriodicTask(Base):
    __tablename__ = "periodic_task"

    name = Column(String(length=120), unique=True, index=True)
    task = Column(String(length=120), index=True)
    crontab_id = Column(Integer, ForeignKey('crontab_schedule.id'), index=True)
    crontab = relationship("CrontabSchedule", back_populates="periodic_tasks")
    interval_id = Column(
        Integer, ForeignKey('interval_schedule.id'), index=True
    )
    interval = relationship(
        "IntervalSchedule", back_populates="periodic_tasks"
    )
    args = Column(String(length=120))
    kwargs = Column(String(length=120))
    last_run_at = Column(
        DateTime, default=datetime.datetime.utcnow, index=True
    )
    total_run_count = Column(Integer, default=0, index=True)
    enabled = Column(Boolean, default=True, index=True)
    no_changes = False

    def __str__(self):
        fmt = '{0.name}: {0.crontab}'
        return fmt.format(self)

    @property
    def schedule(self):
        if self.crontab:
            return self.crontab.schedule
        if self.interval:
            return self.interval.schedule

    def save(self):
        pass


Base.metadata.create_all(engine)
