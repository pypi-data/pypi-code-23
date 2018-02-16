# -*- coding: utf-8 -*-
"""
Settings for Django Authorization are all namespaced in the DJ_AUTH setting.
For example your project's `settings.py` file might look like this:

DJ_AUTH = {
    'content_type_exclude': ('contenttypes.contenttype', 'sessions.session', 'sites.site',
                             'auth.user', 'auth.group', 'auth.permission', 'admin.logentry',
                             'dj_auth.objectfilter',
    ),
    'content_type_include': (),
    'global_fields_exclude':  ('user', ),
    'global_related_fields_exclude': ('fieldname', ),
    'related_filter_fields_exclude': {'auth.user': ('groups', ), },
}

"""
from django.conf import settings


DEFAULT = {
    'content_type_exclude': (),
    'content_type_include': (),
    'global_fields_exclude': (),
    'global_related_fields_exclude': (),
    'related_filter_fields_exclude': {},
}

DJ_AUTH = getattr(settings, 'DJ_AUTH', DEFAULT)
