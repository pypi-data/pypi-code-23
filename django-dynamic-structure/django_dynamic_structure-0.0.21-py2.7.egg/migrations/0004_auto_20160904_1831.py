# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import dyn_struct.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dyn_struct', '0003_auto_20160904_1807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dynamicstructure',
            name='name',
            field=models.CharField(unique=True, max_length=255, verbose_name=b'\xd0\x9d\xd0\xb0\xd0\xb7\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5'),
        ),
        migrations.AlterField(
            model_name='dynamicstructurefield',
            name='classes',
            field=models.CharField(help_text=b'col-md-3, custom-class ...', max_length=255, verbose_name=b'CSS-\xd0\xba\xd0\xbb\xd0\xb0\xd1\x81\xd1\x81\xd1\x8b', blank=True),
        ),
        migrations.AlterField(
            model_name='dynamicstructurefield',
            name='form_field',
            field=models.CharField(blank=True, max_length=255, verbose_name=b'\xd0\x9f\xd0\xbe\xd0\xbb\xd0\xb5', choices=[('Field', 'Field'), ('CharField', 'CharField'), ('IntegerField', 'IntegerField'), ('DateField', 'DateField'), ('TimeField', 'TimeField'), ('DateTimeField', 'DateTimeField'), ('DurationField', 'DurationField'), ('RegexField', 'RegexField'), ('EmailField', 'EmailField'), ('FileField', 'FileField'), ('ImageField', 'ImageField'), ('URLField', 'URLField'), ('BooleanField', 'BooleanField'), ('NullBooleanField', 'NullBooleanField'), ('ChoiceField', 'ChoiceField'), ('MultipleChoiceField', 'MultipleChoiceField'), ('ComboField', 'ComboField'), ('MultiValueField', 'MultiValueField'), ('FloatField', 'FloatField'), ('DecimalField', 'DecimalField'), ('SplitDateTimeField', 'SplitDateTimeField'), ('IPAddressField', 'IPAddressField'), ('GenericIPAddressField', 'GenericIPAddressField'), ('FilePathField', 'FilePathField'), ('SlugField', 'SlugField'), ('TypedChoiceField', 'TypedChoiceField'), ('TypedMultipleChoiceField', 'TypedMultipleChoiceField'), ('UUIDField', 'UUIDField')]),
        ),
        migrations.AlterField(
            model_name='dynamicstructurefield',
            name='form_kwargs',
            field=dyn_struct.db.fields.ParamsField(default=b'{}', verbose_name=b'\xd0\x9f\xd0\xb0\xd1\x80\xd0\xb0\xd0\xbc\xd0\xb5\xd1\x82\xd1\x80\xd1\x8b \xd0\xbf\xd0\xbe\xd0\xbb\xd1\x8f'),
        ),
        migrations.AlterField(
            model_name='dynamicstructurefield',
            name='header',
            field=models.CharField(help_text=b'\xd0\xbf\xd1\x80\xd0\xb8 \xd0\xb7\xd0\xb0\xd0\xbf\xd0\xbe\xd0\xbb\xd0\xbd\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb8 \xd1\x8d\xd1\x82\xd0\xbe\xd0\xb3\xd0\xbe \xd0\xbf\xd0\xbe\xd0\xbb\xd1\x8f, \xd0\xb2\xd0\xbc\xd0\xb5\xd1\x81\xd1\x82\xd0\xbe \xd0\xbf\xd0\xbe\xd0\xbb\xd1\x8f \xd1\x84\xd0\xbe\xd1\x80\xd0\xbc\xd1\x8b \xd0\xb1\xd1\x83\xd0\xb4\xd0\xb5\xd1\x82 \xd0\xb2\xd1\x8b\xd0\xb2\xd0\xbe\xd0\xb4\xd0\xb8\xd1\x82\xd1\x8c \xd0\xb7\xd0\xb0\xd0\xb3\xd0\xbe\xd0\xbb\xd0\xbe\xd0\xb2\xd0\xbe\xd0\xba', max_length=255, verbose_name=b'\xd0\xb7\xd0\xb0\xd0\xb3\xd0\xbe\xd0\xbb\xd0\xbe\xd0\xb2\xd0\xbe\xd0\xba', blank=True),
        ),
        migrations.AlterField(
            model_name='dynamicstructurefield',
            name='name',
            field=models.CharField(unique=True, max_length=255, verbose_name=b'\xd0\x9d\xd0\xb0\xd0\xb7\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5', blank=True),
        ),
        migrations.AlterField(
            model_name='dynamicstructurefield',
            name='position',
            field=models.PositiveSmallIntegerField(verbose_name=b'\xd0\x9f\xd0\xbe\xd0\xb7\xd0\xb8\xd1\x86\xd0\xb8\xd1\x8f \xd0\xb2 \xd1\x81\xd1\x82\xd1\x80\xd0\xbe\xd0\xba\xd0\xb5'),
        ),
        migrations.AlterField(
            model_name='dynamicstructurefield',
            name='row',
            field=models.PositiveSmallIntegerField(verbose_name=b'\xd0\xa1\xd1\x82\xd1\x80\xd0\xbe\xd0\xba\xd0\xb0'),
        ),
        migrations.AlterField(
            model_name='dynamicstructurefield',
            name='structure',
            field=models.ForeignKey(related_name='fields', verbose_name=b'\xd0\xa1\xd1\x82\xd1\x80\xd1\x83\xd0\xba\xd1\x82\xd1\x83\xd1\x80\xd0\xb0', to='dyn_struct.DynamicStructure'),
        ),
        migrations.AlterField(
            model_name='dynamicstructurefield',
            name='widget',
            field=models.CharField(blank=True, max_length=255, verbose_name=b'\xd0\x92\xd0\xb8\xd0\xb4\xd0\xb6\xd0\xb5\xd1\x82', choices=[('Media', 'Media'), ('MediaDefiningClass', 'MediaDefiningClass'), ('Widget', 'Widget'), ('TextInput', 'TextInput'), ('EmailInput', 'EmailInput'), ('URLInput', 'URLInput'), ('NumberInput', 'NumberInput'), ('PasswordInput', 'PasswordInput'), ('HiddenInput', 'HiddenInput'), ('MultipleHiddenInput', 'MultipleHiddenInput'), ('ClearableFileInput', 'ClearableFileInput'), ('FileInput', 'FileInput'), ('DateInput', 'DateInput'), ('DateTimeInput', 'DateTimeInput'), ('TimeInput', 'TimeInput'), ('Textarea', 'Textarea'), ('CheckboxInput', 'CheckboxInput'), ('Select', 'Select'), ('NullBooleanSelect', 'NullBooleanSelect'), ('SelectMultiple', 'SelectMultiple'), ('RadioSelect', 'RadioSelect'), ('CheckboxSelectMultiple', 'CheckboxSelectMultiple'), ('MultiWidget', 'MultiWidget'), ('SplitDateTimeWidget', 'SplitDateTimeWidget'), ('SplitHiddenDateTimeWidget', 'SplitHiddenDateTimeWidget')]),
        ),
        migrations.AlterField(
            model_name='dynamicstructurefield',
            name='widget_kwargs',
            field=dyn_struct.db.fields.ParamsField(default=b'{}', verbose_name=b'\xd0\x9f\xd0\xb0\xd1\x80\xd0\xb0\xd0\xbc\xd0\xb5\xd1\x82\xd1\x80\xd1\x8b \xd0\xb2\xd0\xb8\xd0\xb4\xd0\xb6\xd0\xb5\xd1\x82\xd0\xb0'),
        ),
    ]
