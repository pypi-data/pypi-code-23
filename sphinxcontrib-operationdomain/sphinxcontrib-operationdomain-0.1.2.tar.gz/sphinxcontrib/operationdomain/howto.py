# -*- coding: utf-8 -*-
"""
    sphinx.domains.operation
    ~~~~~~~~~~~~~~~~~~~~~~~~

    The Operation domain.

    :copyright: Copyright 2014 by togakushi
    :license: BSD, see LICENSE for details.
"""

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx import addnodes
from sphinx.domains import Index
from sphinx.locale import l_, _

class OperationHowto(Directive):
    """
    Directive to mark description of a new howto.
    """

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'platform': lambda x: x,
        'synopsis': lambda x: x,
        'reverse': lambda x: x,
        'noindex': directives.flag,
        'deprecated': directives.flag,
    }

    def run(self):
        env = self.state.document.settings.env
        howname = self.arguments[0].strip()
        noindex = 'noindex' in self.options
        env.temp_data['op:howto'] = howname
        ret = []
        if not noindex:
            env.domaindata['op']['howtos'][howname] = \
                (env.docname, self.options.get('synopsis', ''),
                 self.options.get('platform', ''), 'deprecated' in self.options)
            # make a duplicate entry in 'objects' to facilitate searching for
            # the howto in OperationDomain.find_obj()
            env.domaindata['op']['objects'][howname] = (env.docname, 'howto')
            targetnode = nodes.target('', '', ids=['howto-' + howname], ismod=True)
            self.state.document.note_explicit_target(targetnode)
            # the platform and synopsis aren't printed; in fact, they are only
            # used in the modindex currently
            ret.append(targetnode)
            indextext = _('%s (howto)') % howname
            inode = addnodes.index(entries=[('single', indextext, 'howto-' + howname, '', None)])
            ret.append(inode)

            ### 
            if 'reverse' in self.options:
                if self.options.get('platform', ''):
                    revname = '%s (%s)' % (self.options.get('reverse', ''), self.options.get('platform', ''))
                else:
                    revname = self.options.get('reverse', '')
                env.temp_data['op:reverse'] = revname
                env.domaindata['op']['reverses'][revname] = \
                    (env.docname, self.options.get('synopsis', ''),
                     None, 'deprecated' in self.options)
                env.domaindata['op']['objects'][revname] = (env.docname, 'reverse')
                targetnode = nodes.target('', '', ids=['reverse-' + revname],
                                          ismod=True)
                self.state.document.note_explicit_target(targetnode)
                ret.append(targetnode)
                indextext = _('%s (reverse)') % revname
                inode = addnodes.index(entries=[('single', indextext,
                                                 'reverse-' + revname, '', None)])
                ret.append(inode)

        return ret


class OperationHowtoIndex(Index):
    """
    Index subclass to provide the Operation howto index.
    """

    name = 'howtoindex'
    localname = l_('Howto Index')
    shortname = l_('Howto')

    def generate(self, docnames=None):
        content = {}
        # list of all howtos, sorted by howto name
        howtos = sorted(self.domain.data['howtos'].iteritems(),
                         key=lambda x: x[0].lower())
        # sort out collapsable howtos
        prev_howname = ''
        num_toplevels = 0
        for howname, (docname, synopsis, platforms, deprecated) in howtos:
            entries = content.setdefault(howname[0].lower(), [])

            package = howname.split('.')[0]
            if package != howname:
                # it's a subentries
                if prev_howname == package:
                    # first subentries - make parent a group head
                    if entries:
                        entries[-1][1] = 1
                elif not prev_howname.startswith(package):
                    # subentries without parent in list, add dummy entry
                    entries.append([package, 1, '', '', '', '', ''])
                subtype = 2
                entriename = howname.split(package + '.', 1)[1]
            else:
                num_toplevels += 1
                subtype = 0
                entriename = howname

            qualifier = deprecated and _('Deprecated') or ''
            entries.append([entriename, subtype, docname,
                            'howto-' + howname, platforms, qualifier, synopsis])
            prev_howname = howname

        # apply heuristics when to collapse modindex at page load:
        # only collapse if number of toplevel howtos is larger than
        # number of submodules
        collapse = len(howtos) - num_toplevels < num_toplevels

        # sort by first letter
        content = sorted(content.iteritems())

        return content, collapse
