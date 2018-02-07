# -*- coding: utf-8 -*-
"""Setup the tgappcategories application"""
from __future__ import print_function

from tgappcategories import model
from tgext.pluggable import app_model


def bootstrap(command, conf, vars):
    print('Bootstrapping tgappcategories...')

    p = app_model.Permission(permission_name='tgappcategories',
                             description='Permits to manage categories')
    try:
        model.DBSession.add(p)
    except AttributeError:
        # mute ming complaints
        pass
    model.DBSession.flush()