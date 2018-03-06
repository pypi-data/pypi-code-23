# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField, HStoreField, ArrayField

# Create your models here.


class Material(models.Model):
    code = models.CharField(max_length=128, blank=True, null=True, unique=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    unit = models.CharField(max_length=128, blank=True, null=True)
    material_spec = ArrayField(JSONField(null=True, blank=True), null=True, blank=True)
    def __unicode__(self):
        return '{0}-{1}'.format(self.code, self.name)

class MaterialSpecification(models.Model):
    code = models.CharField(max_length=128, blank=True, null=True,  unique=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    material = models.ForeignKey(Material, blank=True, null=True)

    def __unicode__(self):
        return self.name

class MaterialsEntry(models.Model):
    project = JSONField(blank=True, null=True)
    project_unit = JSONField(blank=True, null=True)
    constructionorg = JSONField(blank=True, null=True)
    responsor = JSONField(blank=True, null=True)
    responsor_org = JSONField(blank=True, null=True)
    delivery_order = models.CharField(max_length=128, null=True, blank=True)
    lot_number = models.CharField(max_length=128, null=True, blank=True)
    remark = JSONField(blank=True, null=True)
    material = JSONField(null=True, blank=True)
    material_spec = models.ForeignKey(MaterialSpecification, null=True, blank=True)
    material_count = models.IntegerField(blank=True, null=True, default=1)
    material_value = models.FloatField(blank=True, null=True, default=0.0)
    material_image = JSONField(null=True, blank=True)
    producer = HStoreField(null=True, blank=True)
    supplier = HStoreField(null=True, blank=True)
    location = HStoreField(null=True, blank=True)
    create_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{0}--{1}'.format(self.material.name, self.material_count)

    class Meta:
        ordering = ['create_on']










