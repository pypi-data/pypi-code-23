from typing import List, Optional


# Few constants with necessary data for a slug generation

SLUG_SAVE_AS_DASH = '.,/'
SLUG_ALLOWED_CHARS = r'^[a-zA-Z0-9\-]$'


def get_settings_upload_path(site_id, filename: str) -> str:
    """ Generates full media file name for a theme uploaded file.

    :param site_id: id of the Site instance
    :param filename: file name
    :return: full media file path
    """
    import os
    path = os.path.join(
        'theme-config',
        'site-%s' % site_id,
    )
    if filename is not None:
        path = os.path.join(path, filename)
    return path


def get_settings_upload_url(site_id, filename: str) -> str:
    """ Returns an url for a theme uploaded file.
    """
    from django.core.files.storage import default_storage
    path = get_settings_upload_path(site_id, filename)
    return default_storage.url(path)


def get_theme_asset_upload_path(site_id, filename: str) -> str:
    """ Generates full asset file name for a theme.

    :param site_id: id of the Site instance
    :param filename: file name
    :return: full media file path
    """
    import os
    path = os.path.join(
        'theme-assets',
        'site-%s' % site_id,
    )
    if filename is not None:
        path = os.path.join(path, filename)
    return path


def get_theme_asset_upload_url(site_id, filename: str) -> str:
    """ Returns an url for a theme asset file.
    """
    from django.core.files.storage import default_storage
    path = get_theme_asset_upload_path(site_id, filename)
    return default_storage.url(path)


def slugify_unicode(value: str, save_as_dash: str = SLUG_SAVE_AS_DASH, dash: str = '-') -> str:
    """ Generates a slugify value.

    :param value: original value
    :param save_as_dash: a string which contains characters which must be replaced as dashes
    :param dash: a string which represents a dash symbol
    :return: slugified unicode string
    """
    import re
    import slugify
    for k in save_as_dash:
        value = value.replace(k, dash)
    result = slugify.slugify(value, only_ascii=True)

    pattern = re.compile(SLUG_ALLOWED_CHARS)
    result = ''.join(filter(lambda x: pattern.match(x) is not None, result))
    return result


def get_unique_slug(
        value: str, model_class,
        slug_attr: str = 'slug', slug_func=slugify_unicode,
        ignore_slugs: List[str] = [],
        delimiter: str = '-') -> str:
    """ Generates unique slug for a model.

    :param value: original string value
    :param model_class: model class, for example `Product`
    :param slug_attr: a model attribute name for slug
    :param slug_func: function for generates a slugified value, `slugify_value` by default
    :param ignore_slugs: a list of strings which should be ignored when unique slugify is checking
    :param delimiter: a string which is using as a delimiter before the counter
    :return: slugified unicode string with delimiter and counter if needed
    """
    import itertools
    _slug = _orig = slug_func(value)
    for x in itertools.count(1):
        if not model_class.objects.exclude(
                **{'%s__in' % slug_attr: ignore_slugs}).filter(**{slug_attr: _slug}).exists():
            break
        _slug = '%s%s%d' % (_orig, delimiter, x)
    return _slug


def markdown_to_html(
        source: str,
        extensions: List[str] = []) -> str:
    """ Converts Markdown source code to HTML. Use line break and urlize extensions.

    :param source: Markdown code
    :param extensions: a list of names of additional Markdown extensions
    :return: HTML code
    """
    import markdown
    html = markdown.markdown(
        source,
        extensions=[
            'markdown.extensions.nl2br',
            'urlize',
        ]+extensions)
    return html


def theme_settings_initializer(theme_settings):
    """ Default function which returns the settings scheme usable for theme settings
    component.

    :param theme_settings: ThemeSettings instance, ignored in default implementation
    :return: dict with init scheme
    """
    from .settings import PCART_DEFAULT_THEME_SETTINGS_SCHEMA
    from django.template.loader import render_to_string
    import json
    return json.loads(render_to_string(PCART_DEFAULT_THEME_SETTINGS_SCHEMA))


def theme_settings_assets_initializer(theme_settings):
    """ Returns a list of assets for the particular theme."""
    from .settings import PCART_DEFAULT_THEME_ASSETS_LIST
    return PCART_DEFAULT_THEME_ASSETS_LIST


def decode_multilingual_string(source, language_code_separator=':', languages_delimiter='||'):
    """ Converts a multilingual strings to the dict. For example,

        'en:Welcome||uk:Ласкаво просимо'

    will be converted to a dict

        {'en': 'Welcome', 'uk', 'Ласкаво просимо'}
    """
    return dict(([None]+x.split(language_code_separator, 1))[-2:] for x in source.split(languages_delimiter))


def encode_multilingual_string(source, language_code_separator=':', languages_delimiter='||'):
    """ Converts a dictionary with a set of different localized strings to a single multilingual string.
    For example,

        {'en': 'Welcome', 'uk', 'Ласкаво просимо'}

    will be converted to a string

        'en:Welcome||uk:Ласкаво просимо'
    """
    return languages_delimiter.join(language_code_separator.join(x) for x in source.items())


def get_localized_string(source: str, language_code: Optional[str] = None) -> str:
    """ Converts multilingual string to a simple ordinary string with a single
    particular localization. If `source` contains not a multilingual string but a simple one
    then result will be the same.
    """
    from django.utils.translation import get_language
    current_language = language_code or get_language()
    decoded = decode_multilingual_string(source)
    if current_language in decoded:
        return decoded[current_language]
    elif None in decoded:
        return decoded[None]
    return list(decoded.values())[0]
