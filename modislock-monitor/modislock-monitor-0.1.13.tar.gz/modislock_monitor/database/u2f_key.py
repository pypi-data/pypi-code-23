# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Unicode, Enum, TIMESTAMP, Boolean, TIME
from sqlalchemy.sql import func
from .database import Base


class U2fKey(Base):
    __tablename__ = 'u2f_key'

    key = Column(Integer, primary_key=True, nullable=False)
    handle = Column(Unicode(128), nullable=False, unique=True)
    public_key = Column(Unicode(128), nullable=False)
    counter = Column(Integer, nullable=False)
    transports = Column(Enum('BT', 'BLE', 'NFC', 'USB'))
    enabled = Column(Boolean, nullable=False, default=1)
    created_on = Column(TIMESTAMP, default=func.now(), nullable=False)
    # Foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "U2fKey(key={self.key}, handle={self.handle}, public_key={self.public_key}, " \
               "counter={self.counter}, transports={self.transports}, enabled={self.enabled}, " \
               "created_on={self.created_on}, user_id={self.user_id})".format(self=self)
