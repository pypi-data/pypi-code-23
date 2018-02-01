# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship
from .database import Base


class Door(Base):
    __tablename__ = 'door'

    iddoor = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(Unicode(45), nullable=False)
    pin_num = Column(Integer, nullable=False)
    alt_name = Column(Unicode(45))
    controller_idcontroller = Column(Integer, ForeignKey('controller.idcontroller'))

    door_status = relationship('DoorStatus')
    reader = relationship('Reader')
    relay = relationship('Relay')

    def __repr__(self):
        return "Door(iddoor={self.door}, name={self.name}, " \
               "pin_num={self.pin_num}, alt_name={self.alt_name}, " \
               "controller_idcontroller={self.controller_idcontroller".format(self=self)