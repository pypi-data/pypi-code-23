# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-29 13:29
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


def forwards_func(apps, schema_editor):
    ProductStatus = apps.get_model('pcart_catalog', 'ProductStatus')
    ProductStatusTranslation = apps.get_model('pcart_catalog', 'ProductStatusTranslation')

    for obj in ProductStatus.objects.all():
        ProductStatusTranslation.objects.create(
            master_id=obj.pk,
            language_code=settings.LANGUAGE_CODE,
            title_t=obj.title,
        )


def backwards_func(apps, schema_editor):
    ProductStatus = apps.get_model('pcart_catalog', 'ProductStatus')
    ProductStatusTranslation = apps.get_model('pcart_catalog', 'ProductStatusTranslation')

    for obj in ProductStatus.objects.all():
        translation = _get_translation(obj, ProductStatusTranslation)
        obj.title = translation.title_t
        obj.save()   # Note this only calls Model.save()


def _get_translation(object, ProductStatusTranslation):
    translations = ProductStatusTranslation.objects.filter(master_id=object.pk)
    try:
        # Try default translation
        return translations.get(language_code=settings.LANGUAGE_CODE)
    except ObjectDoesNotExist:
        try:
            # Try default language
            return translations.get(language_code=settings.PARLER_DEFAULT_LANGUAGE_CODE)
        except ObjectDoesNotExist:
            # Maybe the object was translated only in a specific language?
            # Hope there is a single translation
            return translations.get()


class Migration(migrations.Migration):

    dependencies = [
        ('pcart_catalog', '0039_add_translations_to_productstatus'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ]
