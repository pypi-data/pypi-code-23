# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-29 18:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pcart_catalog', '0058_remove_untranslated_fields_from_productvariant'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productvarianttranslation',
            old_name='title_t',
            new_name='title',
        ),
    ]
