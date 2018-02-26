# -*- coding: utf-8 -*-
"""Syntax colorizer

.. module:: client.core.colorizer
   :platform: Windows, Unix
   :synopsis: Syntax colorizer
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

from hydratk.extensions.client.core.tkimport import tk, PYTHON_MAJOR_VERSION

import keyword

if (PYTHON_MAJOR_VERSION == 2):
    import __builtin__ as builtins
else:
    import builtins

class Colorizer(object):
    """Class Colorizer
    """

    _instance = None
    _instance_created = False

    # references
    _config = None

    _patterns = {}

    def __init__(self):
        """Class constructor

        Called when object is initialized

        Args:
           none

        Raises:
           error: ValueError

        """

        if (self._instance_created == False):
            raise ValueError('For creating class instance please use the get_instance method instead!')
        if (self._instance is not None):
            raise ValueError('A Class instance already exists, use get_instance method instead!')

        from hydratk.extensions.client.core.gui import Gui
        self._config = Gui.get_instance().cfg

        self._parse_config()
        self._make_patterns()

    @staticmethod
    def get_instance():
        """Method gets Colorizer singleton instance

        Args:
            none

        Returns:
            obj

        """

        if (Colorizer._instance is None):
            Colorizer._instance_created = True
            Colorizer._instance = Colorizer()

        return Colorizer._instance

    @property
    def config(self):
        """ config property getter """

        return self._config

    def _parse_config(self):
        """Method parses configuration

        Args:
            none

        Returns:
            void

        """

        cfg = self.config.data['Core']['editor']['color']
        self._patterns['keyword'] = {'color' : cfg['keyword']}
        self._patterns['string'] = {'color' : cfg['string']}
        self._patterns['yoda'] = {'color' : cfg['yoda']}

    def _make_patterns(self):
        """Method makes patterns for colorized strings

        Args:
            none

        Returns:
            void

        """

        # keyword
        builtin = [str(name) for name in dir(builtins) if not name.startswith('_')]
        kw = r'\y(' + '|'.join(keyword.kwlist + builtin) + r')\y'
        self._patterns['keyword']['pattern'] = kw

        # string
        stringprefix = r'(\br|u|ur|R|U|UR|Ur|uR|b|B|br|Br|bR|BR)?'
        sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
        dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
        sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
        dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
        string = r'(' + '|'.join([r'#[^\n]*', sq3string, dq3string, sqstring, dqstring]) + r')'
        self._patterns['string']['pattern'] = string

        # yoda
        tags = [
                'TEST-SCENARIO-\d+', 'TEST-CASE-\d+', 'TEST-CONDITION-\d+',
                'ID', 'PATH', 'NAME', 'DESC', 'AUTHOR', 'VERSION',
                'PRE-REQ', 'POST-REQ', 'TEST', 'VALIDATE', 'EVENTS', 'BEFORE_START', 'AFTER_FINISH'
               ]
        yoda = r'\y(' + '|'.join(tags) + r')\y\s*:\s*\|?'
        self._patterns['yoda']['pattern'] = yoda

    def colorize(self, text, start, stop):
        """Method colorizes text

        Args:
            text (obj): Text widget
            start (str): start index
            stop (str): stop index

        Returns:
            bool: yoda tag found

        """

        cnt = tk.IntVar()
        yoda_found = False
        for pattern in ['keyword', 'yoda', 'string']:
            text.tag_remove(pattern, start, stop)
            idx1 = start
            while True:
                # direct Tk call, wrap method search doesn't support nolinestop
                args = [text._w, 'search', '-count', cnt, '-regexp', '-nolinestop']
                if (pattern == 'yoda'):
                    args.append('-nocase')
                args += [self._patterns[pattern]['pattern'], idx1, stop]
                idx1 = str(text.tk.call(tuple(args)))

                if (not idx1):
                    break
                elif (pattern == 'yoda'):
                    yoda_found = True

                idx2 = '{0}+{1}c'.format(idx1, cnt.get())
                text.tag_add(pattern, idx1, idx2)
                idx1 = idx2
            text.tag_config(pattern, foreground=self._patterns[pattern]['color'])

        return yoda_found
