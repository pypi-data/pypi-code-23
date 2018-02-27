# -*- coding: utf-8 -*-
"""
    sphinx.domains.operation
    ~~~~~~~~~~~~~~~~~~~~~~~~

    The Operation domain.

    :copyright: Copyright 2007-2018 by togakushi
    :license: BSD, see LICENSE for details.
"""

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx import addnodes
from sphinx.domains import Index
from sphinx.locale import l_, _

class OperationCommand(Directive):
    """
    Directive to mark description of a new command.
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
        comname = self.arguments[0].strip()
        noindex = 'noindex' in self.options
        env.temp_data['op:command'] = comname
        ret = []

        if not noindex:
            env.domaindata['op']['commands'][comname] = \
                (env.docname, self.options.get('synopsis', ''),
                 self.options.get('platform', ''), 'deprecated' in self.options)
            # make a duplicate entry in 'objects' to facilitate searching for
            # the command in OperationDomain.find_obj()
            env.domaindata['op']['objects'][comname] = (env.docname, 'command')
            targetnode = nodes.target('', '', ids=['command-' + comname], ismod=True)
            self.state.document.note_explicit_target(targetnode)
            # the platform and synopsis aren't printed; in fact, they are only
            # used in the modindex currently
            ret.append(targetnode)
            indextext = _('%s (command)') % comname
            inode = addnodes.index(entries=[('single', indextext,
                                             'command-' + comname, '', None)])
            ret.append(inode)

        if 'reverse' in self.options:
            revname = self.options.get('reverse', '')
            env.temp_data['op:reverse'] = revname
            env.domaindata['op']['reverses'][revname] = \
                (env.docname, self.options.get('synopsis', ''), None, 'deprecated' in self.options)
            env.domaindata['op']['objects'][revname] = (env.docname, 'reverse')
            targetnode = nodes.target('', '', ids=['reverse-' + revname], ismod=True)
            self.state.document.note_explicit_target(targetnode)
            ret.append(targetnode)

        return ret


class OperationCommandIndex(Index):
    """
    Index subclass to provide the Operation command index.
    """

    name = 'commandindex'
    localname = l_('Command Index')
    shortname = l_('Command')

    def generate(self, docnames=None):
        content = {}
        # list of all commands, sorted by command name
        commands = sorted(self.domain.data['commands'].iteritems(),
                         key=lambda x: x[0].lower())
        # sort out collapsable commands
        prev_comname = ''
        num_toplevels = 0
        for comname, (docname, synopsis, platforms, deprecated) in commands:
            entries = content.setdefault(comname[0].lower(), [])

            package = comname.split('/')[0]
            if package != comname:
                # it's a subentries
                if prev_comname == package:
                    # first subentries - make parent a group head
                    if entries:
                        entries[-1][1] = 1
                elif not prev_comname.startswith(package):
                    # subentries without parent in list, add dummy entry
                    entries.append([package, 1, '', '', '', '', ''])
                subtype = 2
                entriename = comname.split(package + '/', 1)[1]
            else:
                num_toplevels += 1
                subtype = 0
                entriename = comname

            qualifier = deprecated and _('Deprecated') or ''
            entries.append([entriename, subtype, docname,
                            'command-' + comname, platforms, qualifier, synopsis])
            prev_comname = comname

        # apply heuristics when to collapse modindex at page load:
        # only collapse if number of toplevel commands is larger than
        # number of submodules
        collapse = len(commands) - num_toplevels < num_toplevels

        # sort by first letter
        content = sorted(content.iteritems())

        return content, collapse
