# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Enum, TIMESTAMP
from sqlalchemy.sql import func
from .database import Base


class DoorStatus(Base):
    __tablename__ = 'door_status'

    iddoor_status = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    status = Column(Enum('ACTIVE', 'INACTIVE'), nullable=False, default='INACTIVE')
    timestamp = Column(TIMESTAMP, nullable=False, default=func.now())
    door_iddoor = Column(Integer, ForeignKey('door.iddoor'), nullable=False)

    def __repr__(self):
        return "DoorStatus(iddoor={self.iddoor}, status={self.status}, " \
               "timestamp={self.timestamp}, door_iddoor={self.door_iddoor}".format(self=self)
