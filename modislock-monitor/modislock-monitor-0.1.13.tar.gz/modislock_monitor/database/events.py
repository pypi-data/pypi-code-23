# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Enum, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Events(Base):
    __tablename__ = 'events'

    id_event = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    event_time = Column(TIMESTAMP, default=func.now(), nullable=False)
    event_type = Column(Enum('USER_CREATED', 'ACCESS', 'DENIED'), nullable=False)
    # Foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    reader_idreader = Column(Integer, ForeignKey('reader.idreader'))

    reader = relationship('Reader')

    def __repr__(self):
        return "Events(id_event={self.id_event}, event_time={self.event_time}, event_type={self.event_type}, " \
               "user_id={self.user_id}, reader_settings_id_reader={self.reader_settings_id_reader})".format(self=self)
