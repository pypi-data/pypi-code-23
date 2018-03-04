# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_maps', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='maps',
            name='layers_control',
            field=models.BooleanField(verbose_name='Layers control', default=True),
        ),
        migrations.AddField(
            model_name='maps',
            name='scale_bar',
            field=models.BooleanField(verbose_name='Scale bar', default=False),
        ),
        migrations.AlterField(
            model_name='maps',
            name='zoom_control',
            field=models.BooleanField(verbose_name='Zoom control', default=True),
        ),
    ]
