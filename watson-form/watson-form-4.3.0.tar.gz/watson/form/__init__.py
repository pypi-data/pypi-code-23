# -*- coding: utf-8 -*-
__version__ = '4.3.0'

try:
    # Fix for setup.py version import
    from watson.form.types import Form, Multipart

    __all__ = ['Form', 'Multipart']
except:  # pragma: no cover
    pass  # pragma: no cover
