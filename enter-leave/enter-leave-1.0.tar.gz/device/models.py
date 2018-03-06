# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField, HStoreField

# Create your models here.
class Device(models.Model):
    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

class DeviceMobility(models.Model):
    project = JSONField(blank=True, null=True)                      #项目名称
    project_unit = JSONField(blank=True, null=True)                 #单位工程

    construction_org = JSONField(blank=True, null=True)             # 施工单位
    construction_per = JSONField(blank=True, null=True)             # 施工单位负责人
    supervising_org = JSONField(blank=True, null=True)              # 监理单位
    supervising_per = JSONField(blank=True, null=True)              # 监理单位负责人

    device_name = models.ForeignKey(Device, blank=True, null=True)          # 设备名称
    code = models.CharField(max_length=255, blank=True, null=True)          # 设备编号
    number = models.IntegerField(blank=True, null=True)                     # 设备数量
    device_type = models.CharField(max_length=255, blank=True, null=True)   # 设备类型
    device_spec = models.CharField(max_length=255, blank=True, null=True)   # 规格型号
    original_value = models.FloatField(blank=True, null=True)               # 原值
    source = models.IntegerField(blank=True, null=True)                     # 1 自有 2 租赁 3 自带
    manufacturer = JSONField(blank=True, null=True)                         # 厂商
    licence = JSONField(blank=True, null=True)                              # 许可证, 对象
    certificate = JSONField(blank=True, null=True)                          # 合格证, 对象

    attachments = JSONField(blank=True, null=True)                          # 附件
    remark = JSONField(blank=True, null=True)                               # 备注, 预留
    is_ground = models.BooleanField()                                       # 进离场
    images = JSONField(blank=True, null=True)                               # 设备照片
    created_on = models.DateTimeField(auto_now_add=True)                    # 进场时间
    end_on = models.DateTimeField(blank=True, null=True)                    # 离场时间