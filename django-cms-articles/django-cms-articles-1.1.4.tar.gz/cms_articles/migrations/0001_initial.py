# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-11 18:21
from __future__ import unicode_literals

import cms.models.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

from cms_articles.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cms', '0013_urlconfrevision'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(editable=False, max_length=255, verbose_name='created by')),
                ('changed_by', models.CharField(editable=False, max_length=255, verbose_name='changed by')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('changed_date', models.DateTimeField(auto_now=True)),
                ('publication_date', models.DateTimeField(blank=True, db_index=True, help_text='When the article should go live. Status must be "Published" for article to go live.', null=True, verbose_name='publication date')),
                ('publication_end_date', models.DateTimeField(blank=True, db_index=True, help_text='When to expire the article. Leave empty to never expire.', null=True, verbose_name='publication end date')),
                ('template', models.CharField(choices=settings.CMS_ARTICLES_TEMPLATES, default=settings.CMS_ARTICLES_TEMPLATES[0][0], help_text='The template used to render the content.', max_length=100, verbose_name='template')),
                ('login_required', models.BooleanField(default=False, verbose_name='login required')),
                ('publisher_is_draft', models.BooleanField(db_index=True, default=True, editable=False)),
                ('languages', models.CharField(blank=True, editable=False, max_length=255, null=True)),
                ('category', models.ForeignKey(help_text='The page the article is accessible at.', on_delete=django.db.models.deletion.CASCADE, related_name='cms_articles', to='cms.Page', verbose_name='category')),
                ('placeholders', models.ManyToManyField(editable=False, related_name='cms_articles', to='cms.Placeholder')),
                ('publisher_public', models.OneToOneField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='publisher_draft', to='cms_articles.Article')),
            ],
            options={
                'ordering': ('-creation_date',),
                'verbose_name': 'article',
                'verbose_name_plural': 'articles',
                'permissions': (('publish_article', 'Can publish page'),),
            },
        ),
        migrations.CreateModel(
            name='ArticlePlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('template', models.CharField(choices=settings.CMS_ARTICLES_PLUGIN_ARTICLE_TEMPLATES, default=settings.CMS_ARTICLES_PLUGIN_ARTICLE_TEMPLATES[0][0], help_text='The template used to render plugin.', max_length=100, verbose_name='Template')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='cms_articles.Article', verbose_name='article')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='ArticlesPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('number', models.IntegerField(default=3, verbose_name='Number of last articles')),
                ('template', models.CharField(choices=settings.CMS_ARTICLES_PLUGIN_ARTICLES_TEMPLATES, default=settings.CMS_ARTICLES_PLUGIN_ARTICLES_TEMPLATES[0][0], help_text='The template used to render plugin.', max_length=100, verbose_name='Template')),
                ('category', models.ForeignKey(blank=True, help_text='Keep empty to show articles from current page, if current page is a category.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='cms.Page', verbose_name='category')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(db_index=True, max_length=15, verbose_name='language')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('page_title', models.CharField(blank=True, help_text='overwrite the title (html title tag)', max_length=255, null=True, verbose_name='title')),
                ('menu_title', models.CharField(blank=True, help_text='overwrite the title in the menu', max_length=255, null=True, verbose_name='title')),
                ('meta_description', models.TextField(blank=True, help_text='The text displayed in search engines.', max_length=155, null=True, verbose_name='description')),
                ('slug', models.SlugField(max_length=255, verbose_name='slug')),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='creation date')),
                ('published', models.BooleanField(default=False, verbose_name='is published')),
                ('publisher_is_draft', models.BooleanField(db_index=True, default=True, editable=False)),
                ('publisher_state', models.SmallIntegerField(db_index=True, default=0, editable=False)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='title_set', to='cms_articles.Article', verbose_name='article')),
                ('excerpt', cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, slotname='excerpt', to='cms.Placeholder')),
                ('publisher_public', models.OneToOneField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='publisher_draft', to='cms_articles.Title')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='title',
            unique_together=set([('language', 'article')]),
        ),
    ]
