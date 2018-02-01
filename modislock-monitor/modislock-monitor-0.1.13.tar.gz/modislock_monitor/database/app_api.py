# coding: utf-8
from sqlalchemy import Column, Unicode
from .database import Base
from sqlalchemy.orm import relationship


class AppApi(Base):
    __tablename__ = 'app_api'

    app_api_id = Column(Unicode(25), primary_key=True, nullable=False)
    app_secret = Column(Unicode(128), nullable=False)
    app_api_access = relationship('AppApiAccess', cascade='all, delete-orphan')

    def __repr__(self):
        return "AppApi(app_api_id={self.app_api_id}, " \
               "app_secret={self.app_secret}".format(self=self)
