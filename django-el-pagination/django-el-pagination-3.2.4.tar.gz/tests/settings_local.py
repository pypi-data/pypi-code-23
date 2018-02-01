

INSTALLED_APPS_LOCAL = (
    'debug_toolbar',
)

INTERNAL_IPS = (
    '127.0.0.1',
    '0.0.0.0',
)

MIDDLEWARE_CLASSES = [
    # ...
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # ...
]

MIDDLEWARE = MIDDLEWARE_CLASSES
'''
    django-debug-toolbar
'''
DEBUG_TOOLBAR_PATCH_SETTINGS = False
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

# This example is unlikely to be appropriate for your project.
CONFIG_DEFAULTS = {
    # Toolbar options
    'RESULTS_STORE_SIZE': 3,
    'SHOW_COLLAPSED': True,
    # Panel options
    'INTERCEPT_REDIRECTS': True,
    'SQL_WARNING_THRESHOLD': 100,  # milliseconds
}

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

