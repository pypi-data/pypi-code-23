from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

# supported language codes (ISO 639-1 to ISO 639-2 mapping)
# see http://dev.viamichelin.com/vm-loading-en.html
VIAMICHELIN_LANGUAGE_MAP = {
    'cs': 'ces',  # Czech
    'da': 'dan',  # Danish
    'de': 'deu',  # German
    'en': 'eng',  # English
    'fi': 'fin',  # Finnish
    'fr': 'fra',  # French
    'it': 'ita',  # Italian
    'nl': 'nld',  # Dutch
    'no': 'nor',  # Norwegian
    'pl': 'pol',  # Polish
    'ro': 'ron',  # Romanian
    'pt': 'por',  # Portuguese
    'es': 'spa',  # Spanish
    'sv': 'swe',  # Swedish
    'tr': 'tur',  # Turkish
}


@register.filter
@stringfilter
def viamichelin(value):
    """
    Turn a long or short language code into an ISO 639-2 language code
    supported by ViaMichelin, unsupported languages into an empty string.
    """
    try:
        iso_639_1 = value[:2]
        return VIAMICHELIN_LANGUAGE_MAP[iso_639_1]
    except KeyError:
        return ''
