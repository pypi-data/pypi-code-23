# -*- coding: utf-8
from django_python3_ldap import utils

from . import models
from .conf import settings


def genomix_search_filters(ldap_fields):
    """Filter LDAP for a given User group

    Args:
        ldap_fields (dict): Dict containing LDAP fields

    Returns:
        str: LDAP Search filter
    """
    ldap_fields["memberOf"] = settings.LDAP_AUTH_SEARCH_FILTER
    search_filters = utils.format_search_filters(ldap_fields)
    return search_filters


def sync_genomix_profile(user, ldap_attributes):
    """Sync User profile attributes for a given Users

    Args:
        user (User instance): User model
        ldap_attributes (dict): Dictionary with LDAP
    """

    if settings.CREATE_PROFILE_ON_SAVE:
        profile_fields = getattr(settings, 'LDAP_AUTH_PROFILE_FIELDS', None)

        if profile_fields:
            defaults = {}
            for key, value in profile_fields.items():
                value = ldap_attributes.get(value, [])
                if len(value) > 0:
                    defaults[key] = value[0]

            models.Profile.objects.update_or_create(
                user=user,
                defaults=defaults
            )
