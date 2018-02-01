# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.sql import func
from .database import Base


class ReaderStatus(Base):
    __tablename__ = 'reader_status'

    id_status = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    timestamp = Column(TIMESTAMP, default=func.now(), nullable=False)
    temp = Column(Integer, nullable=False)
    validation_count = Column(Integer, nullable=False)
    denied_count = Column(Integer, nullable=False)
    reader_idreader = Column(Integer, ForeignKey('reader.idreader'))

    def __repr__(self):
        return "ReaderStatus(id_status={self.id_status}, timestamp={self.timestamp}, " \
               "temp={self.temp}, validation_count={self.validation_count}, " \
               "denied_count={self.denied_count}, " \
               "reader_idreader={self.reader_idreader})".format(self=self)
