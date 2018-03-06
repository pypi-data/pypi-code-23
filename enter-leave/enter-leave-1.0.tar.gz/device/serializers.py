#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests, json
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission

from rest_framework import serializers

from . import models

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Device
        fields = ('id', 'name', 'code')

class DeviceMobilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeviceMobility
        fields = ("id", "project", "project_unit", "construction_org", "construction_per",
                  "supervising_org", "supervising_per", "device_name", "code", "number", "device_type",
                  "device_spec", "original_value", "source", "manufacturer", "licence", "end_on",
                  "certificate", "attachments", "remark", "is_ground", "images", "created_on")

class DeviceMobilityDetailSerializer(DeviceMobilitySerializer):
    device_name = DeviceSerializer(many=False)
