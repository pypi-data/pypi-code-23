# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.sql import func
from .database import Base


class ControllerStatus(Base):
    __tablename__ = 'controller_status'

    idcontroller_status = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    timestamp = Column(TIMESTAMP, nullable=False, default=func.now())
    temp = Column(Integer, nullable=False, default=0)
    validation_count = Column(Integer, nullable=False, default=0)
    denied_count = Column(Integer, nullable=False, default=0)
    controller_idcontroller = Column(Integer, ForeignKey('controller.idcontroller'), nullable=False)

    def __repr__(self):
        return "ControllerStatus(idcontroller={self.idcontroller}, timestamp={self.timestamp}, temp={self.temp}, " \
               "validation_count={self.validation_count}, denied_count={self.denied_count}, " \
               "controller_idcontroller={self.controller_idcontroller}".format(self=self)
