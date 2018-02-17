from django.conf import settings
from django.dispatch import receiver
import os
import datetime
from django.core.cache import cache
from django.db.models.signals import pre_save,pre_delete,post_save
from .models import Site_Abstract, Page_Version, File, Page_Abstract,get_page_site_key
from django.core import serializers
from django.apps import apps
get_model = apps.get_model
from django.utils import timezone

PAGE_PAGE = getattr(settings, 'PAGE_PAGE', 'page.Page')
PAGE_PAGE_CACHE= getattr(settings, 'PAGE_PAGE_CACHE', False) # disable page_cache by default
PAGE_SITE_CACHE= getattr(settings, 'PAGE_SITE_CACHE', False) # disable page_cache by default

USE_BEAUTIFULSOUP = getattr(settings, 'PAGE_SITE_USE_BEAUTIFULSOUP', True)
if USE_BEAUTIFULSOUP:
    from bs4 import BeautifulSoup


@receiver(pre_save, sender=Site_Abstract,dispatch_uid='page_site_pre_save')
def pre_save_site_callback(instance, sender, **kwargs):
    if PAGE_SITE_CACHE:
        cache.delete(get_page_site_key(instance.domain_name))

@receiver(pre_delete, sender=Site_Abstract,dispatch_uid='page_site_pre_delete')
def pre_delete_site_callback(instance, sender, **kwargs):
    if PAGE_SITE_CACHE:
        cache.delete(get_page_site_key(instance.domain_name))

@receiver(post_save,sender=get_model(PAGE_PAGE))
def post_save_page_callback(instance, sender, **kwargs):
    if not issubclass(sender, Page_Abstract):
       return
    version = Page_Version(page=instance)
    version.data = serializers.serialize("json", [instance,])
    version.save()

#@receiver(pre_save, sender=Page_Abstract,dispatch_uid='page_page_pre_save')
@receiver(pre_save,sender=get_model(PAGE_PAGE))
def pre_save_page_callback(instance, sender, **kwargs):
    if not issubclass(sender, Page_Abstract):
       return

    if USE_BEAUTIFULSOUP:
        tree = BeautifulSoup(instance.content, "html.parser")
        instance.content = tree.prettify()
    instance.lastmod = timezone.now()

@receiver(pre_delete, sender=File,dispatch_uid='page_file_pre_delete')
def pre_delete_file_callback(instance, sender, **kwargs):
    try:
        os.remove(instance.file.path)
    except: pass
