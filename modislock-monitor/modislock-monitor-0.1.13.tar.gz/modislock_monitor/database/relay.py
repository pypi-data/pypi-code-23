# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Enum, Boolean
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from .database import Base


class Relay(Base):
    __tablename__ = 'relay'

    idrelay = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    type = Column(Enum('SOLID_STATE', 'MECHANICAL'), nullable=False)
    enabled = Column(Boolean, nullable=False, default=False)
    position = Column(TINYINT, nullable=False)
    delay = Column(Integer, nullable=False, default=1500)
    controller_idcontroller = Column(Integer, ForeignKey('controller.idcontroller'), nullable=False)
    door_iddoor = Column(Integer, ForeignKey('door.iddoor'), nullable=False)
    door = relationship('Door')

    def __repr__(self):
        return "Relay(idrelay={self.idrelay}, type={self.type}, enabled={self.enabled}, " \
               "position={self.position}, delay={self.delay}, " \
               "controller_idcontroller={self.controller_idcontroller}, " \
               "door_iddoor={self.door_iddoor}".format(self=self)