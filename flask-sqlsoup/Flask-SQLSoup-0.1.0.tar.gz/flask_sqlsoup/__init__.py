#!/usr/bin/python3 -tt
# -*- coding: utf-8 -*-

"""
SQLSoup Integration
===================
"""


from sqlsoup import SQLSoup as OriginalSQLSoup
from sqlalchemy import Table, Column


__all__ = ['SQLSoup']


class SQLSoup(OriginalSQLSoup):
    """Register SQLSoup with a Flask application."""

    def __init__(self, app, **kwargs):
        """
        Expects following Flask configuration options:

        ``SQLSOUP_DATABASE_URI = 'sqlite:///:memory:'``
            Database URI to connect to.

        ``SQLSOUP_ROLLBACK_ON_TEARDOWN = True``
            Flag that controls automatic rollback after every request.

        :param app: The Flask application to augment.
        """

        app.config.setdefault('SQLSOUP_DATABASE_URI', 'sqlite:///:memory:')
        app.config.setdefault('SQLSOUP_ROLLBACK_ON_TEARDOWN', True)

        super().__init__(app.config['SQLSOUP_DATABASE_URI'], **kwargs)

        if app.config['SQLSOUP_ROLLBACK_ON_TEARDOWN']:
            @app.teardown_request
            def teardown_request(exn=None):
                app.sqlsoup.session.rollback()

        app.sqlsoup = self


    def map_view(self, name, keys, to=None):
        """
        Map a view, manually specifying list of it's primary keys.

        :param name: Name of the view to map.
        :param keys: Iterable with primary key column names.
        :param to: A name to bind the view to, defaults to ``name``.
        """

        columns = [Column(key, primary_key=True) for key in keys]
        table = Table(name, self._metadata, *columns, autoload=True)
        self.map_to(to or name, selectable=table)


# vim:set sw=4 ts=4 et:
