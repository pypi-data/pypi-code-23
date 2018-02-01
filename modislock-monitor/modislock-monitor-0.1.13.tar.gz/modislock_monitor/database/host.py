# coding: utf-8
from sqlalchemy import Column, Integer, Unicode, Boolean, DATE
from sqlalchemy.orm import relationship
from .database import Base


class Host(Base):
    __tablename__ = 'host'

    idhost = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    serial_number = Column(Unicode(45), nullable=False)
    host_name = Column(Unicode(45), nullable=False)
    installation_date = Column(DATE, nullable=False)
    registered = Column(Boolean, nullable=False)

    controller = relationship('Controller', cascade='all, delete-orphan')
    host_sensors = relationship('HostSensors', cascade='all, delete-orphan')
    settings = relationship('Settings', cascade='all, delete-orphan')

    def __repr__(self):
        return "Host(idhost={self.idhost}, serial_number={self.serial_number}, " \
               "host_name={self.host_name},installation_date={self.installation_date}, " \
               "registered={self.registered}".format(self=self)
