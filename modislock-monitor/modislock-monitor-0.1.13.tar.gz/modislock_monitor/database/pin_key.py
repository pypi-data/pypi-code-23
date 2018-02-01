# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, TIMESTAMP, Boolean
from sqlalchemy.sql import func
from .database import Base


class PinKey(Base):
    """PinCode

    Table holds the protocol PIN. Is used for pin codes and references the user they are assigned to.

    """
    __tablename__ = 'pin_key'

    key = Column(Integer, primary_key=True, nullable=False)
    enabled = Column(Boolean, nullable=False, default=1)
    created_on = Column(TIMESTAMP, default=func.now(), nullable=False)
    # Foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "PinKey(key={self.key}, enabled={self.enabled}, created_on={self.created_on}," \
               " user_id={self.user_id})".format(self=self)
