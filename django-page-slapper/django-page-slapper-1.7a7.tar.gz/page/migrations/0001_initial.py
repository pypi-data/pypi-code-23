# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime
import page.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(max_length=255, upload_to=page.models.upload_file_to)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.CharField(max_length=100, db_index=True)),
                ('title', models.CharField(max_length=100, verbose_name=b'Menu Title')),
                ('show_in_menu', models.BooleanField(default=False)),
                ('priority', models.IntegerField(default=0)),
                ('html_title', models.CharField(max_length=100, null=True, blank=True)),
                ('content', models.TextField()),
                ('members_only', models.BooleanField(default=False)),
                ('lastmod', models.DateTimeField(default=datetime.datetime.now)),
                ('sitemap', models.BooleanField(default=True, verbose_name=b'Share a link to this page with search engines')),
            ],
            options={
                'abstract': False,
                'permissions': (('change_show_in_menu', 'change_show_in_menu'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page_Editor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('page', models.ForeignKey(to='page.Page')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('title', models.CharField(max_length=200)),
                ('domain_name', models.CharField(max_length=300, serialize=False, primary_key=True)),
                ('default_domain', models.BooleanField(default=False)),
                ('meta_data', models.TextField(null=True, blank=True)),
                ('footer', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UUID_File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(max_length=255, upload_to=page.models.upload_uuid_file_to)),
                ('uuid', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='page',
            name='site',
            field=models.ForeignKey(to='page.Site'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='file',
            name='page',
            field=models.ForeignKey(related_name=b'page_file', to='page.Page'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Page_User',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.user',),
        ),
        migrations.AddField(
            model_name='page_editor',
            name='editor',
            field=models.ForeignKey(to='page.Page_User'),
            preserve_default=True,
        ),
    ]
