# -*- coding: utf-8 -*-
"""Text formatter

.. module:: client.core.formatter
   :platform: Windows, Unix
   :synopsis: Text formatter
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

from hydratk.extensions.client.core.tkimport import tk

class Formatter(object):
    """Class Formatter
    """

    _instance = None
    _instance_created = False

    # references
    _config = None

    # format
    _patterns = {}
    _amend_keys = {}

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
        """Method gets Formatter singleton instance

        Args:
            none

        Returns:
            obj

        """

        if (Formatter._instance is None):
            Formatter._instance_created = True
            Formatter._instance = Formatter()

        return Formatter._instance

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

        cfg = self.config.data['Core']['editor']['format']
        self._patterns['python_inc'] = {'indent' : cfg['indent_python']}
        self._patterns['python_dec'] = {'indent' :-cfg['indent_python']}
        self._patterns['yoda'] = {'indent' : cfg['indent_yoda']}

    def _make_patterns(self):
        """Method makes patterns for text formatting

        Args:
            none

        Returns:
            void

        """

        # python increase
        tags = [
                'def', 'class', 'if', 'elif', 'else', 'while', 'for', 'with', 'try', 'except', 'finally'
               ]
        self._patterns['python_inc']['pattern'] = r'\y(' + '|'.join(tags) + r')\y\s*.*:'
        
        # python decrease
        tags = [
                'return', 'break', 'continue', 'pass', 'exit', 'raise'
               ]
        self._patterns['python_dec']['pattern'] = r'\y(' + '|'.join(tags) + r')\y\s+.*'

        # yoda
        tags = [
                'TEST-SCENARIO-\d+', 'TEST-CASE-\d+', 'TEST-CONDITION-\d+', 'PRE-REQ', 'POST-REQ',
                'TEST', 'VALIDATE', 'EVENTS', 'BEFORE_START', 'AFTER_FINISH'
               ]
        self._patterns['yoda']['pattern'] = r'\y(' + '|'.join(tags) + r')\y\s*:\s*\|?'
        
        # keys to be amended
        self._amend_keys = {
                            '(' : ')',
                            '{' : '}',
                            '[' : ']'
                           }

    def format_text(self, event, text):
        """Method formats text

        Args:
            event (obj): event
            text (obj): Text widget

        Returns:
            void

        """

        if (event.keysym == 'Return'):
            self._indent(text)
        elif (event.char in self._amend_keys):
            self._amend_key(event.char, text)
            
    def _amend_key(self, key, text):
        """Method amends predefined key

        Args:
            key (str): key
            text (obj): Text widget

        Returns:
            void

        """

        text.insert(tk.INSERT, self._amend_keys[key])

    def _indent(self, text):
        """Method sets indent

        Args:
            text (obj): Text widget

        Returns:
            void

        """

        row, col = text.index(tk.INSERT).split('.')
        start, stop = '{0}.0'.format(int(row) - 1), '{0}.0-1c'.format(row)
        content = text.get(start, stop)
        indent = len(content) - len(content.lstrip())

        for key, value in self._patterns.items():
            nocase = True if (key == 'yoda') else False
            idx = text.search(value['pattern'], start, stopindex=stop, nocase=nocase, regexp=True)
            if (idx):
                indent += value['indent']
                if (indent < 0):
                    indent = 0
                break

        text.insert(tk.INSERT, ' ' * indent)
