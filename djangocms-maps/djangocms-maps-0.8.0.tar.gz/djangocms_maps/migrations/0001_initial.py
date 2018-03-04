# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='Maps',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(related_name='djangocms_maps_maps', primary_key=True, to='cms.CMSPlugin',
                                                       serialize=False, parent_link=True, auto_created=True)),
                ('map_provider', models.CharField(verbose_name='map provider', max_length=16, choices=[
                    ('mapbox', 'Mapbox OSM (API key required)'),
                    ('bingmaps', 'Bing Maps (API key required)'),
                    ('googlemaps', 'Google Maps (API key required)'),
                    ('here', 'HERE WeGo (API key required)'),
                    ('viamichelin', 'ViaMichelin (API key required)')], default='mapbox')),
                ('title', models.CharField(verbose_name='map title', max_length=100, null=True, blank=True)),
                ('address', models.CharField(verbose_name='address', max_length=150)),
                ('zipcode', models.CharField(verbose_name='zip code', max_length=30)),
                ('city', models.CharField(verbose_name='city', max_length=100)),
                ('content', models.CharField(help_text='Displayed under address in the bubble.',
                                             verbose_name='additional content', max_length=255, blank=True)),
                ('style', models.TextField(help_text='Provide a valid JSON configuration (escaped). '
                                                     'See developers.google.com/maps/documentation/javascript/styling',
                                           verbose_name='custom map style', blank=True)),
                ('zoom', models.PositiveSmallIntegerField(verbose_name='zoom level', default=13, choices=[
                    (0, '0'),
                    (1, '1'),
                    (2, '2'),
                    (3, '3'),
                    (4, '4'),
                    (5, '5'),
                    (6, '6'),
                    (7, '7'),
                    (8, '8'),
                    (9, '9'),
                    (10, '10'),
                    (11, '11'),
                    (12, '12'),
                    (13, '13'),
                    (14, '14'),
                    (15, '15'),
                    (16, '16'),
                    (17, '17'),
                    (18, '18'),
                    (19, '19'),
                    (20, '20'),
                    (21, '21')])),
                ('lat', models.DecimalField(help_text='Use latitude & longitude to fine tune the map position.',
                                            blank=True, verbose_name='latitude', null=True, max_digits=10, decimal_places=6)),
                ('lng', models.DecimalField(verbose_name='longitude', max_digits=10, null=True, blank=True, decimal_places=6)),
                ('route_planer_title', models.CharField(verbose_name='route planner title', max_length=150, null=True,
                                                        blank=True, default='Calculate your fastest way to here')),
                ('route_planer', models.BooleanField(verbose_name='route planner', default=False)),
                ('width', models.CharField(help_text='Plugin width (in px, em, %).', verbose_name='width', max_length=6, default='100%')),
                ('height', models.CharField(help_text='Plugin height (in px, em).', verbose_name='height', max_length=6, default='400px')),
                ('info_window', models.BooleanField(help_text='Show textbox over marker', verbose_name='info window', default=True)),
                ('scrollwheel', models.BooleanField(help_text='Enable scrollwheel zooming on the map', verbose_name='scrollwheel', default=True)),
                ('double_click_zoom', models.BooleanField(verbose_name='double click zoom', default=True)),
                ('draggable', models.BooleanField(verbose_name='draggable', default=True)),
                ('keyboard_shortcuts', models.BooleanField(verbose_name='keyboard shortcuts', default=True)),
                ('pan_control', models.BooleanField(verbose_name='Pan control', default=True)),
                ('zoom_control', models.BooleanField(verbose_name='zoom control', default=True)),
                ('street_view_control', models.BooleanField(verbose_name='Street View control', default=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
