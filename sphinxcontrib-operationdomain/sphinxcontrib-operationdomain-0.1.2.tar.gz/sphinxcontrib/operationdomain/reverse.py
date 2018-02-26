# -*- coding: utf-8 -*-
"""
    sphinx.domains.operation
    ~~~~~~~~~~~~~~~~~~~~~~~~

    The Operation domain.

    :copyright: Copyright 2014 by togakushi
    :license: BSD, see LICENSE for details.
"""

from sphinx.domains import Index
from sphinx.locale import l_, _

class OperationReverseIndex(Index):
    """
    Index subclass to provide the Operation reverse index.
    """

    name = 'reverseindex'
    localname = l_('Reverse Index')
    shortname = l_('Reverse')

    def generate(self, docnames=None):
        content = {}
        # list of all reverses, sorted by reverse name
        reverses = sorted(self.domain.data['reverses'].iteritems(),
                         key=lambda x: x[0].lower())
        # sort out collapsable reverses
        prev_revname = ''
        num_toplevels = 0
        for revname, (docname, synopsis, platforms, deprecated) in reverses:
            entries = content.setdefault(revname[0].lower(), [])

            package = revname.split('.')[0]
            if package != revname:
                # it's a subentries
                if prev_revname == package:
                    # first subentries - make parent a group head
                    if entries:
                        entries[-1][1] = 1
                elif not prev_revname.startswith(package):
                    # subentries without parent in list, add dummy entry
                    entries.append([package, 1, '', '', '', '', ''])
                subtype = 2
                entriename = revname.split(package + '.', 1)[1]
            else:
                num_toplevels += 1
                subtype = 0
                entriename = revname

            qualifier = deprecated and _('Deprecated') or ''
            entries.append([entriename, subtype, docname,
                            'reverse-' + revname, platforms, qualifier, synopsis])
            prev_revname = revname

        # apply heuristics when to collapse modindex at page load:
        # only collapse if number of toplevel reverses is larger than
        # number of submodules
        collapse = len(reverses) - num_toplevels < num_toplevels

        # sort by first letter
        content = sorted(content.iteritems())

        return content, collapse
