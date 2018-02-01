# coding: utf-8
from sqlalchemy import Column, Unicode, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class AppApiAccess(Base):

    __tablename__ = 'app_api_access'

    token = Column(Unicode(128), primary_key=True, nullable=False)
    expires = Column(TIMESTAMP, nullable=False)
    app_api_app_api_id = Column(Unicode(25), ForeignKey('app_api.app_api_id'), nullable=False)

    def __repr__(self):
        return "AppApiAccess(token={self.token}, expires={self.expires}, " \
               "app_api_app_api_id={self.app_api_app_api_id}".format(self=self)