#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import json
from json import JSONEncoder

from rest_framework import serializers
from rest_framework_mongoengine import serializers as mongo_serializer
from rest_framework.fields import empty


class BaseSerializer(serializers.Serializer):
    pass


class BaseModelSerializer(serializers.ModelSerializer):
    pass


class BaseMongoSerializer(mongo_serializer.DocumentSerializer):
    pass
