from django.db import models
from django.contrib.sites.models import Site
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _
from typing import Optional, Dict
import uuid


class ThemeSettings(models.Model):
    """ Represents a theme settings component."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.OneToOneField(Site, verbose_name=_('Site'), on_delete=models.PROTECT, related_name='settings')

    data = JSONField(_('Data'), default=dict, blank=True)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Theme settings')
        verbose_name_plural = _('Theme settings')

    def __str__(self) -> str:
        return str(self.site)

    def get_upload_path(self, filename: Optional[str] = None) -> str:
        """ Returns the upload path for the specified file."""
        from .utils import get_settings_upload_path
        return get_settings_upload_path(self.site_id, filename)

    def get_settings_fields(self) -> Dict:
        """ Returns a dictionary with an information about theme settings form schema."""
        from django.core.files.storage import default_storage
        from django.utils.module_loading import import_string
        from .settings import PCART_THEME_SETTINGS_SCHEME_INITIALIZER
        storage = default_storage

        # Loads the init scheme
        _initializer = import_string(PCART_THEME_SETTINGS_SCHEME_INITIALIZER)
        result = _initializer(self)

        _current = self.data.get('current', {})  # Read the current settings state

        for group in result:
            # Looping over all groups
            for o in group.get('settings', []):
                if 'id' in o:
                    if o.get('type') in ['radio', 'select', 'text', 'collection', 'blog', 'link_list', 'color', 'textarea']:
                        o['value'] = _current.get(o['id'], o.get('default', ''))
                    elif o.get('type') in ['image']:
                        value = _current.get(o['id'], o.get('default', ''))
                        if value:
                            value = self.get_upload_path(value)
                            o['url'] = storage.url(value)
                        o['value'] = value
                    elif o.get('type') in ['checkbox']:
                        o['value'] = _current.get(o['id'], o.get('default', False))
        return result

    def generate_assets(self):
        """ Generates templated assets if necessary."""
        from django.utils.module_loading import import_string
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        from django.template.loader import render_to_string
        from .utils import get_theme_asset_upload_path
        from .settings import PCART_THEME_SETTINGS_ASSETS_INITIALIZER
        storage = default_storage

        # Loads the assets list
        _initializer = import_string(PCART_THEME_SETTINGS_ASSETS_INITIALIZER)
        result = _initializer(self)

        context = {
            'settings': self.data.get('current', {}),
            'site': self.site,
        }
        for asset in result:
            asset_src = render_to_string('assets/%s' % asset, context=context)
            file_name = get_theme_asset_upload_path(self.site_id, asset)
            storage.delete(file_name)
            storage.save(file_name, ContentFile(asset_src))

    def get_all_assets(self):
        from django.utils.module_loading import import_string
        from .settings import PCART_THEME_SETTINGS_ASSETS_INITIALIZER
        from .utils import get_theme_asset_upload_url
        # Loads the assets list
        _initializer = import_string(PCART_THEME_SETTINGS_ASSETS_INITIALIZER)
        files_list = _initializer(self)
        return [get_theme_asset_upload_url(self.site_id, x) for x in files_list]

    def get_assets_with_extension(self, extension='css'):
        return [x for x in self.get_all_assets() if x.endswith('.'+extension)]

    def save(self, *args, **kwargs):
        """ Generates assets if needed after saving.
        """
        super(ThemeSettings, self).save(*args, **kwargs)
        self.generate_assets()


class RootFile(models.Model):
    """ Represents a root file, like robots.txt or humans.txt. Also may be usable
    for some files which some services are promising to place into the site root folder
    for checking ownership or something like that.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, verbose_name=_('Site'), on_delete=models.PROTECT, related_name='root_files')

    file_name = models.CharField(_('File name'), max_length=255)
    content = models.TextField(_('Content'), default='', blank=True)
    content_type = models.CharField(_('Content type'), default='text/plain', max_length=70)
    base64_decode = models.BooleanField(
        _('Base64 decode'), default=False,
        help_text=_('Use this option if you use binary data encoded with Base64 instead a plain text.')
    )

    cache_timeout = models.PositiveIntegerField(_('Cache timeout (seconds)'), default=3600)

    published = models.BooleanField(_('Published'), default=True)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Root file')
        verbose_name_plural = _('Root files')
        unique_together = ['site', 'file_name']

    def __str__(self) -> str:
        return self.file_name

    def save(self, *args, **kwargs):
        """ Drops the particular cache record when a file has been saved.
        """
        self.clear_cache()
        super(RootFile, self).save(*args, **kwargs)

    def cache_key(self) -> str:
        """ Generates the key for the cache record which contains the file content.
        """
        return 'rootfile-%s-%s' % (self.site_id, self.file_name)

    def clear_cache(self):
        """ Drops the cache record which contains the file content.
        """
        from django.core.cache import cache
        cache.delete(self.cache_key())

    def view(self, request):
        """ Returns the HttpResponse with the particular file content.
        """
        from django.http import HttpResponse
        from django.core.cache import cache
        response = cache.get(self.cache_key())
        if response is None:
            content = self.content
            if self.base64_decode:
                """ Use Base64 decoding if the file content is a Base64 encoded
                binary data.
                """
                import base64
                content = base64.b64decode(content)
            response = HttpResponse(content, content_type=self.content_type)
            cache.set(self.cache_key(), response, self.cache_timeout)
        return response
