# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import sys
import logging
import json
from functools import wraps
from sqlalchemy.ext.declarative import ConcreteBase, AbstractConcreteBase, DeferredReflection
from sqlalchemy.ext.declarative.api import declared_attr
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy import MetaData
from sqlalchemy import text
from sqlalchemy import func
from sqlalchemy.orm import load_only

from .data import Base

__all__ = ["Base", "BaseModel", "create_table", ]


class BaseModel(AbstractConcreteBase, Base):
    _item = None

    # @classmethod
    # def create_model(cls, item=None, *args, **kwargs):
    #     model = cls(item, *args, **kwargs)
    #     return model

    @classmethod
    def save(cls, item=None, **kwargs):
        model = cls()
        model._item = item
        model.setup(item=item, **kwargs)
        return model

    @property
    def item(self):
        if self._item is not None:
            return self._item
        self._item = {}
        return self._item

    def get_field_value(self, field, default=None, **kwargs):
        if field in kwargs:
            return kwargs.get(field, default=default)
        return self.item.get(field, default)

    def setup(self, item, **kwargs):
        raise NotImplementedError


def create_table(engine, model):
    if model and engine and isinstance(model, Base):
        model.metadata.create_all(bind=engine)
    return True

