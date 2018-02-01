# coding: utf-8
from sqlalchemy import Column, Integer
from .database import Base


class Recent24hApprovedCount(Base):
    __tablename__ = "recent_24h_approved_count"

    approved_count = Column(Integer, nullable=False, default=0, primary_key=True)

    def __repr__(self):
        return "Recent24hApprovedCount(approved_count={self.approved_count})".format(self=self)
