from django.conf import settings


# A function which initializes a theme settings form
PCART_THEME_SETTINGS_SCHEME_INITIALIZER = getattr(
    settings, 'PCART_THEME_SETTINGS_SCHEME_INITIALIZER',
    'pcart_core.utils.theme_settings_initializer',
)


# Default template name which is using for describes a theme settings form
PCART_DEFAULT_THEME_SETTINGS_SCHEMA = getattr(
    settings, 'PCART_DEFAULT_THEME_SETTINGS_SCHEMA',
    'pcart/settings_schema.json',
)


PCART_THEME_SETTINGS_ASSETS_INITIALIZER = getattr(
    settings, 'PCART_THEME_SETTINGS_ASSETS_INITIALIZER',
    'pcart_core.utils.theme_settings_assets_initializer',
)


PCART_DEFAULT_THEME_ASSETS_LIST = getattr(
    settings, 'PCART_DEFAULT_THEME_ASSETS_LIST', [],
)
