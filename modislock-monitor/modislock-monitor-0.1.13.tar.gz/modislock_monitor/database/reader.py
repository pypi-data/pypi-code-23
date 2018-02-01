# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Unicode, Enum, FLOAT
from sqlalchemy.orm import relationship
from .database import Base


class Reader(Base):
    __tablename__ = 'reader'

    idreader = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(Unicode(45), nullable=False)
    status = Column(Enum('ACTIVE', 'INACTIVE'), nullable=False)
    pin_num = Column(Integer, nullable=False, default=0)
    alt_name = Column(Unicode(45))
    location = Column(Unicode(45))
    location_direction = Column(Enum('ENTRY', 'EXIT'))
    uuid = Column(Unicode(45))
    software_version = Column(Unicode(10))
    validation_count = Column(Integer)
    denied_count = Column(Integer)
    controller_address = Column(Integer, nullable=False)

    controller_idcontroller = Column(Integer,
                                     ForeignKey('controller.idcontroller'),
                                     nullable=False)
    door_iddoor = Column(Integer, ForeignKey('door.iddoor'), nullable=False)

    events = relationship('Events', cascade='all, delete-orphan')
    reader_status = relationship('ReaderStatus', cascade='all, delete-orphan')

    def __repr__(self):
        return "Reader(idreader={self.reader}, name={self.name}, status={self.status}, " \
               "alt_name={self.alt_name}, uuid={self.uuid}, " \
               "validation_count={self.validation_count}, denied_count={self.denied_count}, " \
               "controller_idcontroller={self.controller_idcontroller}, " \
               "door_iddoor={self.door_iddoor})".format(self=self)

