# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OverallRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.IntegerField(db_index=True)),
                ('rating', models.DecimalField(null=True, max_digits=6, decimal_places=1)),
                ('category',
                    models.IntegerField(
                        null=True,
                        choices=[
                            (1, b'maps.Map-map'),
                            (2, b'documents.Document-document'),
                            (3, b'layers.Layer-layer')])),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.IntegerField(db_index=True)),
                ('rating', models.IntegerField()),
                ('timestamp', models.DateTimeField(default=datetime.datetime.now)),
                ('category',
                    models.IntegerField(
                        null=True,
                        choices=[
                            (1, b'maps.Map-map'),
                            (2, b'documents.Document-document'),
                            (3, b'layers.Layer-layer')])),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('overall_rating',
                    models.ForeignKey(related_name='ratings', to='agon_ratings.OverallRating', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='rating',
            unique_together=set([('object_id', 'content_type', 'user', 'category')]),
        ),
        migrations.AlterUniqueTogether(
            name='overallrating',
            unique_together=set([('object_id', 'content_type', 'category')]),
        ),
    ]
