# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Canton',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('code', models.CharField(max_length=16, unique=True, verbose_name='Code')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
            ],
            options={
                'verbose_name_plural': 'Cantons',
                'verbose_name': 'Canton',
            },
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('code', models.CharField(max_length=16, unique=True, verbose_name='Code')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('canton', models.ForeignKey(verbose_name='Canton', to='crdist.Canton')),
            ],
            options={
                'verbose_name_plural': 'Districts',
                'verbose_name': 'District',
            },
        ),
        migrations.CreateModel(
            name='Province',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('code', models.CharField(max_length=16, unique=True, verbose_name='Code')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
            ],
            options={
                'verbose_name_plural': 'Provinces',
                'verbose_name': 'Province',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='Name')),
            ],
            options={
                'verbose_name_plural': 'Regions',
                'verbose_name': 'Region',
            },
        ),
        migrations.AddField(
            model_name='district',
            name='region',
            field=models.ForeignKey(verbose_name='Region', null=True, to='crdist.Region'),
        ),
        migrations.AddField(
            model_name='canton',
            name='province',
            field=models.ForeignKey(verbose_name='Province', to='crdist.Province'),
        ),
    ]
