# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-29 13:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pcart_catalog', '0042_rename_translatable_fields_for_productstatus'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title_t', models.CharField(max_length=255, unique=True, verbose_name='Title')),
                ('description_t', models.TextField(blank=True, verbose_name='Description')),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='pcart_catalog.Vendor')),
            ],
            options={
                'verbose_name': 'Vendor Translation',
                'db_tablespace': '',
                'default_permissions': (),
                'db_table': 'pcart_catalog_vendor_translation',
                'managed': True,
            },
        ),
        migrations.AlterUniqueTogether(
            name='vendortranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
