# coding: utf-8
from sqlalchemy import Column, Integer
from .database import Base


class Recent24hDeniedCount(Base):
    __tablename__ = "recent_24h_denied_count"

    denied_count = Column(Integer, nullable=False, default=0, primary_key=True)

    def __repr__(self):
        return "Recent24hDeniedCount(denied_count={self.denied_count})".format(self=self)
