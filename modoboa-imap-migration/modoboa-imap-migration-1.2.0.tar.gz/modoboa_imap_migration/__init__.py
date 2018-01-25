# -*- coding: utf-8 -*-

"""A plugin to migrate mailboxes using IMAP."""

from __future__ import unicode_literals

from pkg_resources import get_distribution, DistributionNotFound


try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

default_app_config = "modoboa_imap_migration.apps.IMAPMigrationConfig"
