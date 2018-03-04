# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pushapp', '0002_auto_20150514_0057'),
    ]

    operations = [
        migrations.AddField(
            model_name='apnsdevice',
            name='is_paid',
            field=models.BooleanField(db_index=True, verbose_name='Is paid', default=False, editable=False),
        ),
    ]
