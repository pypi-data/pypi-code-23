# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship
from .database import Base


class HostSensors(Base):
    __tablename__ = 'host_sensors'

    idhost_sensors = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
    name = Column(Unicode(45), nullable=True)
    location = Column(Unicode(45), nullable=False)
    host_idhost = Column(Integer, ForeignKey('host.idhost'))

    host_status = relationship('HostStatus', cascade='all, delete-orphan')

    def __repr__(self):
        return "HostStatus(idhost_sensors={self.idhost_sensors}, name={self.name}, " \
               "location={self.location}, host_idhost={self.host_idhost}".format(self=self)