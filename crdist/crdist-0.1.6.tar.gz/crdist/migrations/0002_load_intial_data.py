# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.core.management import call_command
import os

fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures'))
fixture_filename = 'data.json'


def load_fixture(apps, schema_editor):
    fixture_file = os.path.join(fixture_dir, fixture_filename)
    call_command('loaddata', fixture_file) 


class Migration(migrations.Migration):

    dependencies = [
        ('crdist', '0001_initial'),
    ]

    operations = [
                  migrations.RunPython(load_fixture),
    ]
