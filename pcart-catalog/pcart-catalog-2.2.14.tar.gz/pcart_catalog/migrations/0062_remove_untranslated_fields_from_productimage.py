# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-29 18:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pcart_catalog', '0061_migrate_translatable_fields_for_productimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productimage',
            name='title',
        ),
    ]
