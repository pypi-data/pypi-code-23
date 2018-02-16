# Copyright 2011-2018 Rumma & Ko Ltd
# License: BSD, see LICENSE for more details.
"""
This is the :mod:`etgen` package.

Inspired by Frederik Lundh's
`ElementTree Builder
<http://effbot.org/zone/element-builder.htm>`_

.. autosummary::
   :toctree:

   html
   html2rst
   intervat
   odf
   sepa
   utils


>>> E = Namespace('http://my.ns',
...    "bar baz bar-o-baz foo-bar class def".split())

>>> bob = E.bar_o_baz()
>>> baz = E.add_child(bob, 'baz', class_='first')
>>> print E.tostring(baz)
<baz xmlns="http://my.ns" class="first" />

>>> bob = E.bar_o_baz('Hello', class_='first', foo_bar="3")
>>> print E.tostring(bob)
<bar-o-baz xmlns="http://my.ns" class="first" foo-bar="3">Hello</bar-o-baz>

The following reproduces a pifall. Here is the initial code:

>>> E = Namespace(None, "div br".split())
>>> bob = E.div("a", E.br(), "b", E. br(), "c", E.br(), "d")
>>> print E.tostring(bob)
<div>a<br />b<br />c<br />d</div>

The idea is to use :func:`join_elems` to insert the <br> tags:

>>> from etgen.utils import join_elems

But surprise:

>>> elems = join_elems(["a", "b", "c", "d"], sep=E.br())
>>> print E.tostring(E.div(*elems))
<div>a<br />bcd<br />bcd<br />bcd</div>

What happened here is that the same `<br>` element instance was being
inserted multiple times at different places.  The correct usage is
without the parentheses so that `join_elems` instantiates each time a
new element:

>>> elems = join_elems(["a", "b", "c", "d"], sep=E.br)
>>> print E.tostring(E.div(*elems))
<div>a<br />b<br />c<br />d</div>



"""

import os

from .setup_info import SETUP_INFO

fn = os.path.join(os.path.dirname(__file__), 'setup_info.py')
exec(compile(open(fn, "rb").read(), fn, 'exec'))

__version__ = SETUP_INFO['version']

intersphinx_urls = dict(docs="http://etgen.lino-framework.org")
srcref_url = 'https://github.com/lino-framework/etgen/blob/master/%s'

