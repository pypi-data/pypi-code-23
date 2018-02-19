#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import json
import codecs
import logging

logger = __import__('logging').getLogger(__name__)


class Recipe(object):

    def __init__(self, buildout, name, options,):
        self.name = name
        self.filename = options['output-file']
        self.contents = self._process_section(
            buildout, options['contents-section']
        )

    def install(self):
        with codecs.open(self.filename, 'w', 'utf-8') as f:
            json.dump(self.contents, f, indent=4,
                      separators=(',', ': '), sort_keys=True)
        return self.filename

    def update(self):
        return self.install()

    def _process_section(self, buildout, section):
        _me = {}
        section = buildout[section]
        for option in section:
            if '-section' in option:
                name = option.replace('-section', '')
                _me[name] = self._process_section(buildout, section[option])
            elif section[option] in ("true", "True"):
                _me[option] = True
            elif section[option] in ("false", "False"):
                _me[option] = False
            else:
                _me[option] = []
                for _o in section[option].split('\n'):
                    _me[option].append(_o.strip())
                    if '-section' in _me[option][-1]:
                        _me[option][-1] = self._process_section(
                            buildout, _me[option][-1].replace('-section', '')
                        )
                if len(_me[option]) == 1:
                    _me[option] = _me[option][0]
                elif _me[option][-1] == '**end-list**':
                    del _me[option][-1]
        return _me
