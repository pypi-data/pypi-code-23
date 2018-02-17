# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Page_Version',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('saved', models.DateTimeField(default=datetime.datetime.now)),
                ('data', models.TextField()),
                ('page', models.ForeignKey(to='page.Page')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
