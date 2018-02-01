# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Unicode, TIMESTAMP, Boolean
from sqlalchemy.sql import func
from .database import Base


class RfidKey(Base):
    """RFIDCode

    Table holds the protocol for RFID tags. References back to user they are assigned to.

    """
    __tablename__ = 'rfid_key'

    key = Column(Unicode(128), primary_key=True, unique=True, nullable=False)
    enabled = Column(Boolean, nullable=False, default=1)
    created_on = Column(TIMESTAMP, default=func.now(), nullable=False)
    # Foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "RfidKey(key={self.key}, enabled={self.enabled}, created_on={self.created_on}," \
               " user_id={self.user_id})".format(self=self)