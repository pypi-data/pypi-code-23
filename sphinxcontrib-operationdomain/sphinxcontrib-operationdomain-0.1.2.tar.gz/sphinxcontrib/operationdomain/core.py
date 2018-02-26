# -*- coding: utf-8 -*-
"""
    sphinx.domains.operation
    ~~~~~~~~~~~~~~~~~~~~~~~~

    The Operation domain.

    :copyright: Copyright 2014 by togakushi
    :license: BSD, see LICENSE for details.
"""

import re

from sphinx.roles import XRefRole
from sphinx.locale import l_, _
from sphinx.domains import Domain, ObjType
from sphinx.util.nodes import make_refnode
from sphinx.util.docfields import Field, TypedField

from sphinxcontrib.operationdomain.command import OperationCommand, OperationCommandIndex
from sphinxcontrib.operationdomain.setting import OperationSetting, OperationSettingIndex
from sphinxcontrib.operationdomain.install import OperationInstall, OperationInstallIndex
from sphinxcontrib.operationdomain.reverse import OperationReverseIndex
from sphinxcontrib.operationdomain.howto import OperationHowto, OperationHowtoIndex


# REs for Operation signatures
op_sig_re = re.compile(
    r'''^ ([\w.]*\.)?            # class name(s)
          (\w+)  \s*             # thing name
          (?: \((.*)\)           # optional: arguments
          )? $                   # and nothing more
          ''', re.VERBOSE)


class OperationXRefRole(XRefRole):
    def process_link(self, env, refnode, has_explicit_title, title, target):
        refnode['op:command'] = env.temp_data.get('op:command')
        refnode['op:setting'] = env.temp_data.get('op:setting')
        refnode['op:install'] = env.temp_data.get('op:install')
        refnode['op:howto'] = env.temp_data.get('op:howto')
        if not has_explicit_title:
            title = title.lstrip('.')   # only has a meaning for the target
            target = target.lstrip('~') # only has a meaning for the title
            # if the first character is a tilde, don't display the command/class
            # parts of the contents
            if title[0:1] == '~':
                title = title[1:]
                dot = title.rfind('.')
                if dot != -1:
                    title = title[dot+1:]
        # if the first character is a dot, search more specific namespaces first
        # else search builtins first
        if target[0:1] == '.':
            target = target[1:]
            refnode['refspecific'] = True
        return title, target


class OperationDomain(Domain):
    """Operation domain."""

    name = 'op'
    label = 'Operation'

    object_types = {
        'command':       ObjType(l_('command'),        'command'),
        'setting':       ObjType(l_('setting'),        'setting'),
        'install':       ObjType(l_('install'),        'install'),
        'howto':         ObjType(l_('howto'),           'howto'),
    }

    directives = {
        'command':         OperationCommand,
        'setting':         OperationSetting,
        'install':         OperationInstall,
        'howto':           OperationHowto,
    }

    roles = {
        'command':   OperationXRefRole(),
        'setting':   OperationXRefRole(),
        'install':   OperationXRefRole(),
        'howto':     OperationXRefRole(),
    }

    initial_data = {
        'objects': {},  # fullname -> docname, objtype
        'commands': {}, # comname -> comname, synopsis, platform, deprecated
        'settings': {}, # setname -> setname, synopsis, platform, deprecated
        'installs': {}, # insname -> insname, synopsis, platform, deprecated
        'reverses': {}, # revname -> revname, synopsis, platform, deprecated
        'howtos': {},   # howname -> howname, synopsis, platform, deprecated
    }

    indices = [
        OperationHowtoIndex,
        OperationCommandIndex,
        OperationSettingIndex,
        OperationInstallIndex,
        OperationReverseIndex,
    ]

    types = {
        'command': 'commands',
        'setting': 'settings',
        'install': 'installs',
        'reverse': 'reverses',
        'howto': 'howtos',
    }

    def clear_doc(self, docname):
        for fullname, (fn, _) in self.data['objects'].items():
            if fn == docname:
                del self.data['objects'][fullname]
        for comname, (fn, _, _, _) in self.data['commands'].items():
            if fn == docname:
                del self.data['commands'][comname]
        for setname, (fn, _, _, _) in self.data['settings'].items():
            if fn == docname:
                del self.data['settings'][setname]
        for insname, (fn, _, _, _) in self.data['installs'].items():
            if fn == docname:
                del self.data['installs'][insname]
        for revname, (fn, _, _, _) in self.data['reverses'].items():
            if fn == docname:
                del self.data['reverses'][revname]
        for howname, (fn, _, _, _) in self.data['howtos'].items():
            if fn == docname:
                del self.data['howtos'][howname]

    def find_obj(self, env, comname, setname, insname, revname, howname, name, type, searchmode=0):
        """Find a Operation object for "name", perhaps using the given command
           Returns a list of (name, object entry) tuples.
        """

        if not name:
            return []

        objects = self.data['objects']
        matches = []

        newname = None
        if searchmode == 1:
            objtypes = self.objtypes_for_role(type)
            if objtypes is not None:
                if not newname:
                    if comname and comname + '.' + name in objects and \
                       objects[comname + '.' + name][1] in objtypes:
                        newname = comname + '.' + name
                    elif setname and setname + '.' + name in objects and \
                       objects[setname + '.' + name][1] in objtypes:
                        newname = setname + '.' + name
                    elif insname and insname + '.' + name in objects and \
                       objects[insname + '.' + name][1] in objtypes:
                        newname = insname + '.' + name
                    elif revname and revname + '.' + name in objects and \
                       objects[revname + '.' + name][1] in objtypes:
                        newname = revname + '.' + name
                    elif howname and howname + '.' + name in objects and \
                       objects[howname + '.' + name][1] in objtypes:
                        newname = howname + '.' + name
                    elif name in objects and objects[name][1] in objtypes:
                        newname = name
                    else:
                        # "fuzzy" searching mode
                        searchname = '.' + name
                        matches = [(oname, objects[oname]) for oname in objects
                                   if oname.endswith(searchname)
                                   and objects[oname][1] in objtypes]
        else:
            # NOTE: searching for exact match, object type is not considered
            if name in objects:
                newname = name
            elif comname and comname + '.' + name in objects:
                newname = comname + '.' + name
            elif setname and setname + '.' + name in objects:
                newname = setname + '.' + name
            elif insname and insname + '.' + name in objects:
                newname = insname + '.' + name
            elif revname and revname + '.' + name in objects:
                newname = revname + '.' + name
            elif howname and howname + '.' + name in objects:
                newname = howname + '.' + name
        if newname is not None:
            matches.append((newname, objects[newname]))
        return matches

    def resolve_xref(self, env, fromdocname, builder, type, target, node, contnode):
        comname = node.get('op:command')
        setname = node.get('op:setting')
        insname = node.get('op:install')
        revname = node.get('op:reverse')
        howname = node.get('op:howto')
        searchmode = node.hasattr('refspecific') and 1 or 0
        matches = self.find_obj(env, comname, setname, insname, revname, howname, target, type, searchmode)

        if not matches:
            return None
        elif len(matches) > 1:
            env.warn_node(
                'more than one target found for cross-reference '
                '%r: %s' % (target, ', '.join(match[0] for match in matches)),
                node)
        name, obj = matches[0]

        if obj[1] == type:
            # get additional info for howtos
            docname, synopsis, platform, deprecated = self.data[self.types[type]][name]
            assert docname == obj[0]
            title = name
            if synopsis:
                title += ': ' + synopsis
            if deprecated:
                title += _(' (deprecated)')
            if platform:
                title += ' (' + platform + ')'
            return make_refnode(builder, fromdocname, docname, type + '-' + name, contnode, title)
        else:
            return make_refnode(builder, fromdocname, obj[0], name, contnode, name)

    def get_objects(self):
        for x, y in self.types.iteritems():
            for objname, info in self.data[y].iteritems():
                yield (objname, objname, x, info[0], x + '-' + objname, 0)
        for refname, (docname, type) in self.data['objects'].iteritems():
            yield (refname, refname, type, docname, refname, 1)
