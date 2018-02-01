# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.sql import func
from .database import Base


class HostStatus(Base):
    __tablename__ = 'host_status'

    idhost_status = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    reading = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, default=func.now(), nullable=False)
    host_sensors_idhost_sensors = Column(Integer, ForeignKey('host_sensors.idhost_sensors'))

    def __repr__(self):
        return "HostStatus(idhost_status={self.idhost_status}, " \
               "reading={self.reading}, timestamp={self.timestamp}, " \
               "host_sensors_idhost_sensors={self.host_sensors_idhost_sensors}".format(self=self)
