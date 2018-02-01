# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, TIME
from sqlalchemy.dialects.mysql import TINYINT
from .database import Base


class Rules(Base):
    """Individual key rules

    """
    __tablename__ = 'rules'

    id_rules = Column(Integer, primary_key=True, autoincrement=True)
    days = Column(TINYINT(unsigned=True))
    start_time = Column(TIME)
    end_time = Column(TIME)
    readers = Column(TINYINT(unsigned=True))

    # Foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "Rules(id_rules={self.id_rules}, days={self.days}, " \
               "start_time={self.start_time}, end_time={self.end_time}, " \
               "readers={self.readers})".format(self=self)
