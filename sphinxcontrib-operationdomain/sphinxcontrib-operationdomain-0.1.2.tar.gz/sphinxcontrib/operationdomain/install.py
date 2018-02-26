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

class OperationInstall(Directive):
    """
    Directive to mark description of a new install.
    """

    has_content = False
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
        insname = self.arguments[0].strip()
        noindex = 'noindex' in self.options
        env.temp_data['op:install'] = insname
        ret = []
        if not noindex:
            env.domaindata['op']['installs'][insname] = \
                (env.docname, self.options.get('synopsis', ''),
                 self.options.get('platform', ''), 'deprecated' in self.options)
            # make a duplicate entry in 'objects' to facilitate searching for
            # the install in OperationDomain.find_obj()
            env.domaindata['op']['objects'][insname] = (env.docname, 'install')
            targetnode = nodes.target('', '', ids=['install-' + insname],
                                      ismod=True)
            self.state.document.note_explicit_target(targetnode)
            # the platform and synopsis aren't printed; in fact, they are only
            # used in the modindex currently
            ret.append(targetnode)
            indextext = _('%s (install)') % insname
            inode = addnodes.index(entries=[('single', indextext,
                                             'install-' + insname, '', None)])
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


class OperationInstallIndex(Index):
    """
    Index subclass to provide the Operation install index.
    """

    name = 'installindex'
    localname = l_('Install Index')
    shortname = l_('Install')

    def generate(self, docnames=None):
        content = {}
        # list of all installs, sorted by install name
        installs = sorted(self.domain.data['installs'].iteritems(),
                         key=lambda x: x[0].lower())
        # sort out collapsable installs
        prev_insname = ''
        num_toplevels = 0
        for insname, (docname, synopsis, platforms, deprecated) in installs:
            entries = content.setdefault(insname[0].lower(), [])

            package = insname.split('.')[0]
            if package != insname:
                # it's a subentries
                if prev_insname == package:
                    # first subentries - make parent a group head
                    if entries:
                        entries[-1][1] = 1
                elif not prev_insname.startswith(package):
                    # subentries without parent in list, add dummy entry
                    entries.append([package, 1, '', '', '', '', ''])
                subtype = 2
                entriename = insname.split(package + '.', 1)[1]
            else:
                num_toplevels += 1
                subtype = 0
                entriename = insname

            qualifier = deprecated and _('Deprecated') or ''
            entries.append([entriename, subtype, docname,
                            'install-' + insname, platforms, qualifier, synopsis])
            prev_insname = insname

        # apply heuristics when to collapse modindex at page load:
        # only collapse if number of toplevel installs is larger than
        # number of submodules
        collapse = len(installs) - num_toplevels < num_toplevels

        # sort by first letter
        content = sorted(content.iteritems())

        return content, collapse
