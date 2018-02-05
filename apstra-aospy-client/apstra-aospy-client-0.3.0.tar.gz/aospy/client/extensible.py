# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

import six
from pkg_resources import iter_entry_points
from first import first

if six.PY2:
    from itertools import ifilter
else:
    ifilter = filter


__all__ = ['Extensible']


class Extensible(object):
    extension_groups = []

    @property
    def extensions(self):
        return [ep.name for group in self.extension_groups
                for ep in iter_entry_points(group)]

    def extend(self, attrname, plugin_cls):
        """
        extend the current instance with a new attribute called `attrname`
        that is a plugin of class `plugin_cls`.  This allows for adhoc
        additions of plugins to client instances (vs. using entry-point groups)
        """
        setattr(self, attrname, plugin_cls(self))
        return getattr(self, attrname)

    def extension_install(self, extension_name):
        """
        Find the `extension_name` in any of the associated groups
        and then extend the running instance with this new plugin.
        """
        ep = first(ep for group in self.extension_groups
                   for ep in iter_entry_points(group, extension_name))

        if not ep:
            raise AttributeError('no extension named "%s"' % extension_name)

        plugin = ep.load()
        if not plugin:
            raise RuntimeError(
                'extension "%s" not supported on this version' %
                extension_name)

        return self.extend(extension_name, plugin)

    def extensions_autoload(self):
        all_eps = ifilter(None, (ep for group in self.extension_groups
                                 for ep in iter_entry_points(group)))

        for ep in all_eps:
            plugin = ep.load()
            setattr(self, ep.name, plugin(self))

    def __getattr__(self, extension_name):
        """
        If caller attempts to reference a non-existing attribute on the
        instance, then attempt to find a plugin from the associated groups
        and auto-extend if one is found.
        """
        return self.extension_install(extension_name)
