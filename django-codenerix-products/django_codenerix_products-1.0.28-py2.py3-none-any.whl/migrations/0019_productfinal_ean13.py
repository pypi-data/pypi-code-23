# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-10 14:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codenerix_products', '0018_auto_20170508_0911'),
    ]

    operations = [
        migrations.AddField(
            model_name='productfinal',
            name='ean13',
            field=models.CharField(blank=True, max_length=13, null=True, verbose_name='EAN-13'),
        ),
    ]
