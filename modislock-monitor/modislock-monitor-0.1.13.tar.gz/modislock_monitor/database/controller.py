# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from .database import Base


class Controller(Base):
    __tablename__ = 'controller'

    idcontroller = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    uuid = Column(Unicode(45))
    software_version = Column(Unicode(10))
    name = Column(Unicode(45), nullable=False)
    port = Column(Unicode(45), nullable=False)
    baud_rate = Column(Integer, nullable=False, default=115200)
    data_bits = Column(TINYINT, nullable=False, default=8)
    stop_bits = Column(TINYINT, nullable=False, default=1)
    host_idhost = Column(Integer, ForeignKey('host.idhost'), nullable=False)

    reader = relationship('Reader', cascade='all, delete-orphan')
    door = relationship('Door', cascade='all, delete-orphan')
    relay = relationship('Relay', cascade='all, delete-orphan')
    controller_status = relationship('ControllerStatus', cascade='all, delete-orphan')

    def __repr__(self):
        return "Controller(idcontroller={self.idcontroller}, uuid={self.uuid}, " \
               "name={self.name}, port={self.port}, baud_rate={self.baud_rate}, " \
               "data_bits={self.data_bits}, stop_bits={self.stop_bits}, " \
               "host_idhost={self.host_idhost}".format(self=self)
