# coding: utf-8
from sqlalchemy import Column, Enum, Unicode
from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy.sql import func
from .database import Base


class Recent24hEvents(Base):
    __tablename__ = 'recent_24h_events'

    first_name = Column(Unicode(50), nullable=False, primary_key=True)
    last_name = Column(Unicode(50), nullable=False)
    event_type = Column(Enum('USER_CREATED', 'ACCESS', 'DENIED'), nullable=False)
    event_time = Column(TIMESTAMP, default=func.now(), nullable=False)
    location = Column(Unicode(45))
    location_direction = Column(Unicode(45))

    def __repr__(self):
        return "Recent24hEvents(first_name={self.first_name}, last_name={self.last_name}, " \
               "event_type={self.event_time}, event_time={self.event_time}, location={self.location}, " \
               "location_direction={self.location_direction}".format(self=self)
