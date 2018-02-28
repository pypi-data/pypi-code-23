# -*- coding: utf-8 -*-

import model
import containers


def create(parent):
    """create the stl library"""
    import model.cc
    kwargs = {}
    kwargs['parent'] = parent
    kwargs['name'] = 'stl'

    library = model.Library(**kwargs)

    kwargs['parent'] = library
    kwargs['name'] = 'std'
    namespace = model.cc.Namespace(**kwargs)

    containers.create(namespace)