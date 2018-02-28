# -*- coding: utf-8 -*-

from beatle.model import Library
from beatle.model.cc import Namespace
from . import containers

def create(parent):
    """create the stl library"""
    kwargs = {}
    kwargs['parent'] = parent
    kwargs['name'] = 'stl'

    library = Library(**kwargs)

    kwargs['parent'] = library
    kwargs['name'] = 'std'
    namespace = Namespace(**kwargs)

    containers.create(namespace)