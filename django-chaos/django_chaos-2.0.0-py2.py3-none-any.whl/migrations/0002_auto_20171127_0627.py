# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import chaos.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('chaos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Type', to='chaos.ProjectType'),
        ),
        migrations.AlterField(
            model_name='task',
            name='responsible',
            field=models.ForeignKey(related_name='tasks', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.ForeignKey(related_name='tasks', on_delete=django.db.models.deletion.PROTECT, default=chaos.models.default_task_status, verbose_name='Status', to='chaos.TaskStatus'),
        ),
    ]
