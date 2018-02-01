# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from .database import Base


class SettingsValues(Base):
    __tablename__ = 'settings_values'

    id_values = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    value = Column(Unicode(45), nullable=False)

    settings_id_settings = Column(Integer, ForeignKey('settings.id_settings'), nullable=False)

    def __repr__(self):
        return "SettingsValues(id_values={self.id_values}, value={self.value}, " \
               "settings_id_settings={self.settings_id_settings})".format(self=self)
