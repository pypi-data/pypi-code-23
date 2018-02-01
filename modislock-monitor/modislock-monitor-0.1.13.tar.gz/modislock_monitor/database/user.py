# coding: utf-8
from sqlalchemy import Column, Integer, Unicode, Boolean
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """User table

    Defines login information but is also referenced in all available protocols

    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(Unicode(50), nullable=False)
    last_name = Column(Unicode(50), nullable=False)
    email = Column(Unicode(50), unique=True)
    password = Column(Unicode(128))
    is_admin = Column(Boolean, nullable=False, default=0)

    # Relationships
    rules = relationship('Rules', cascade='all, delete-orphan')
    pin_key = relationship('PinKey', cascade='all, delete-orphan')
    rfid_key = relationship('RfidKey', cascade='all, delete-orphan')
    event = relationship('Events', cascade='all, delete-orphan')
    otp_key = relationship('OtpKey', cascade='all, delete-orphan')
    u2f_key = relationship('U2fKey', cascade='all, delete-orphan')

    def __repr__(self):
        return "User(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, " \
               "password={self.password}, email={self.email}, is_admin={self.is_admin})".format(self=self)
