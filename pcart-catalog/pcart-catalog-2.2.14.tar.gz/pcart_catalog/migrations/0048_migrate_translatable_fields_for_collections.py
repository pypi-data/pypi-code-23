# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-29 14:37
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


def forwards_func(apps, schema_editor):
    Collection = apps.get_model('pcart_catalog', 'Collection')
    CollectionTranslation = apps.get_model('pcart_catalog', 'CollectionTranslation')

    for obj in Collection.objects.all():
        CollectionTranslation.objects.create(
            master_id=obj.pk,
            language_code=settings.LANGUAGE_CODE,
            title_t=obj.title,
            description_t=obj.description,
            page_title_t=obj.page_title,
            meta_description_t=obj.meta_description,
            meta_keywords_t=obj.meta_keywords,
            meta_text_t=obj.meta_text,
        )


def backwards_func(apps, schema_editor):
    Collection = apps.get_model('pcart_catalog', 'Collection')
    CollectionTranslation = apps.get_model('pcart_catalog', 'CollectionTranslation')

    for obj in Collection.objects.all():
        translation = _get_translation(obj, CollectionTranslation)
        obj.title = translation.title_t
        obj.description = translation.meta_description_t
        obj.page_title = translation.page_title_t
        obj.meta_description = translation.meta_description_t
        obj.meta_keywords = translation.meta_keywords_t
        obj.meta_text = translation.meta_text_t
        obj.save()   # Note this only calls Model.save()


def _get_translation(object, CollectionTranslation):
    translations = CollectionTranslation.objects.filter(master_id=object.pk)
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
        ('pcart_catalog', '0047_add_translations_to_collections'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ]
