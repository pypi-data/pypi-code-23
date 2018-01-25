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
    pass
    # @classmethod
    # def create_model(cls, item=None, *args, **kwargs):
    #     model = cls(item, *args, **kwargs)
    #     return model


def create_table(engine, model):
    if model and engine and isinstance(model, Base):
        model.metadata.create_all(bind=engine)
    return True

