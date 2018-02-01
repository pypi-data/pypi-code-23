# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Unicode, Enum
from sqlalchemy.orm import relationship
from .database import Base


class Settings(Base):
    __tablename__ = 'settings'

    id_settings = Column(Integer, primary_key=True, autoincrement=True)
    settings_name = Column(Unicode(45), unique=True)
    units = Column(Unicode(45), nullable=False)
    # Foreign keys
    settings_group_name = Column(Enum('WEB', 'READERS', 'MONITOR', 'RULES'), nullable=False)
    host_idhost = Column(Integer, ForeignKey('host.idhost'), nullable=False)

    settings_values = relationship('SettingsValues', cascade='all, delete-orphan')

    def __repr__(self):
        return "Settings(id_settings={self.id_settings}, settings_name={self.settings_name}, " \
               "units={self.units})".format(self=self)
