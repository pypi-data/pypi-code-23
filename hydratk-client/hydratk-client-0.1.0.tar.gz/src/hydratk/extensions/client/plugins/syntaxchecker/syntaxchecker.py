# -*- coding: utf-8 -*-
"""Syntax checker plugin

.. module:: client.plugins.syntaxchecker
   :platform: Windows, Unix
   :synopsis: Syntax checker
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

from hydratk.extensions.client.core import plugin

from yaml import safe_load
from yaml.scanner import ScannerError
from yaml.parser import ParserError
import traceback

class Plugin(plugin.Plugin):
    """Class Plugin
    """

    def _init_plugin(self):
        """Method initializes plugin

        Args:
           none

        Returns:
           void

        """

        self._plugin_id = 'syntaxchecker'
        self._plugin_name = 'SyntaxChecker'
        self._plugin_version = '0.1.0'
        self._plugin_author = 'Petr Rašek <bowman@hydratk.org>, HydraTK team <team@hydratk.org>'
        self._plugin_year = '2017 - 2018'

    def _setup(self):
        """Method executes plugin setup

        Args:
           none

        Returns:
           void

        """

        self._set_menu_item('plugin', 'htk_syntaxchecker_menu', self._check_syntax)

    def _check_syntax(self, event=None):
        """Method checks syntax

        Args:
            event (obj): event

        Returns:
            void

        """

        tab = self.editor.nb.get_current_tab()
        if (tab != None):
            path = tab.path
            if (path != None):
                self.logger.debug(self.trn.msg('htk_syntaxchecker_start', path))
                res, error = self._check(path, tab)

                if (res):
                    self.logger.info(self.trn.msg('htk_syntaxchecker_success'))
                else:
                    self.logger.warn(self.trn.msg('htk_syntaxchecker_error', error))

    def _check(self, path, tab):
        """Method checks syntax

        Args:
            path (str): file path
            tab (obj): FileTab reference

        Returns:
            tuple: result (bool), error (str)

        """

        suffix = path.split('.')[-1]
        if (suffix == 'py'):
            result, error = self._check_python(tab.name, tab.text.get('1.0', 'end-1c'))
        elif (suffix in ['jedi', 'padawan']):
            result, error = self._check_jedi(tab.name, tab.text.get('1.0', 'end-1c'))
        else:
            result, error = True, ''

        return result, error

    def _check_python(self, name, content):
        """Method checks python file

        Args:
            name (str): filename
            content (str): file content

        Returns:
            tuple: result (bool), error (str)

        """

        result, error = True, ''
        try:
            src = content.replace('# -*- coding: utf-8 -*-', '')
            compile(src, name, 'exec')
        except Exception:
            result, error = False, '\n' + '\n'.join(traceback.format_exc().splitlines()[3:])

        return result, error

    def _check_jedi(self, name, content):
        """Method checks jedi file

        Args:
            name (str): filename
            content (str): file content

        Returns:
            tuple: result (bool), error (str)

        """

        try:
            content = safe_load(content)
        except (ScannerError, ParserError):
            return False, 'Invalid YAML structure'

        test = self._reformat_test(content)

        error = ''
        for i in range(1, len(test.keys()) + 1):
            tsc_id = 'test-scenario-%d' % i
            if (tsc_id in test):
                error += self._check_scenario(tsc_id, test[tsc_id])
            else:
                error += '\nMissing tag {0}'.format(tsc_id)

        result = True if (error == '') else False

        return result, error

    def _reformat_test(self, content):
        """Method reformats test content

        Recursive traversal, lowercase keys

        Args:
            content (dict): structure

        Returns:
            tuple: result (bool), error (str)

        """

        test = {}
        for key, value in content.items():
            test[key.lower()] = self._reformat_test(value) if (type(value) is dict) else value

        return test

    def _check_scenario(self, id, content):
        """Method checks scenario

        Args:
            id (str): id tag
            content (dict): structure

        Returns:
            str: error

        """

        error = ''
        keys = content.keys()
        for tag in ['id', 'name']:
            if (tag not in keys):
                error += '\n{0}: Missing tag {1}'.format(id, tag)

        for tag in ['pre-req', 'post-req']:
            if (tag in keys):
                error += self._check_python_block([id, tag], content[tag])

        if ('events' in keys):
            for key, value in content['events'].items():
                error += self._check_python_block([id, 'events', key], value)

        tca_ids = []
        for key in keys:
            if ('test-case-' in key):
                tca_ids.append(key)

        for i in range(1, len(tca_ids) + 1):
            tca_id = 'test-case-%d' % i
            if (tca_id in tca_ids):
                error += self._check_case([id, tca_id], content[tca_id])
            else:
                error += '\n{0}: Missing tag {1}'.format(id, tca_id)

        return error

    def _check_case(self, ids, content):
        """Method checks case

        Args:
            ids (list): id tags
            content (dict): structure

        Returns:
            str: error

        """

        error = ''
        keys = content.keys()
        for tag in ['id', 'name']:
            if (tag not in keys):
                error += '\n{0}: Missing tag {1}'.format(':'.join(ids), tag)

        if ('events' in keys):
            for key, value in content['events'].items():
                error += self._check_python_block(ids + ['events', key], value)

        tco_ids = []
        for key in keys:
            if ('test-condition-' in key):
                tco_ids.append(key)

        for i in range(1, len(tco_ids) + 1):
            tco_id = 'test-condition-%d' % i
            if (tco_id in tco_ids):
                error += self._check_condition(ids + [tco_id], content[tco_id])
            else:
                error += '\n{0}: Missing tag {1}'.format(':'.join(ids), tco_id)

        return error

    def _check_condition(self, ids, content):
        """Method checks condition

        Args:
            ids (list): id tags
            content (dict): structure

        Returns:
            str: error

        """

        error = ''
        keys = content.keys()
        for tag in ['id', 'name', 'test', 'validate']:
            if (tag not in keys):
                error += '\n{0}: Missing tag {1}'.format(':'.join(ids), tag)

        if ('events' in keys):
            for key, value in content['events'].items():
                error += self._check_python_block(ids + ['events', key], value)

        for tag in ['test', 'validate']:
            if (tag in keys):
                error += self._check_python_block(ids + [tag], content[tag])

        if ('validate' in keys and 'assert' not in content['validate']):
            error += '\n{0}: Missing assertion'.format(':'.join(ids + ['validate']))

        return error

    def _check_python_block(self, ids, content):
        """Method checks Python code block

        Args:
            ids (str): id tags
            content (str): code

        Returns:
            str: error

        """

        error = ''
        try:
            compile(content, ':'.join(ids), 'exec')
        except Exception:
            error = '\n{0}'.format('\n'.join(traceback.format_exc().splitlines()[3:]))

        return error
