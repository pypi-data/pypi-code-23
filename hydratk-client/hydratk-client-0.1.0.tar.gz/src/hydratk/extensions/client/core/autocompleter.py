# -*- coding: utf-8 -*-
"""Automatic code completion

.. module:: client.core.autocompleter
   :platform: Windows, Unix
   :synopsis: Automatic code completion
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

import sys
from jedi import settings, Script

from hydratk.extensions.client.core.tkimport import tk, ttk

class AutoCompleter(object):
    """Class AutoCompleter
    """

    _instance = None
    _instance_created = False

    # references
    _root = None
    _config = None
    _tab = None

    # gui elements
    _win = None
    _tree = None
    _vbar = None

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
        self._root = Gui.get_instance()
        self._config = self.root.cfg

        self._parse_config()

    @staticmethod
    def get_instance():
        """Method gets AutoCompleter singleton instance

        Args:
            none

        Returns:
            obj

        """

        if (AutoCompleter._instance is None):
            AutoCompleter._instance_created = True
            AutoCompleter._instance = AutoCompleter()

        return AutoCompleter._instance

    @property
    def root(self):
        """ root property getter """

        return self._root

    @property
    def config(self):
        """ config property getter """

        return self._config

    @property
    def tab(self):
        """ tab property getter """

        return self._tab

    def _parse_config(self):
        """Method parses configuration

        Args:
            none

        Returns:
            void

        """

        settings.case_insensitive_completion = False
        self.update_pythonpath()

    def update_pythonpath(self):
        """Method updates Python path

        Args:
            none

        Returns:
            void

        """
        
        if (self.config.data['Projects'] != None):
            for project in self.config.data['Projects'].values():
                for p in project['pythonpath']:
                    if (p not in sys.path):
                        sys.path.append(p)

    def _set_gui(self, completions):
        """Method sets graphical interface

        Args:
            completions (list): code completions

        Returns:
            void

        """
        
        self._win = tk.Toplevel(self.root)
        self._win.title('')
        self._win.geometry('+%d+%d' % (self.root.winfo_screenwidth() / 3, self.root.winfo_screenheight() / 3))
        self._win.tk.call('wm', 'iconphoto', self._win._w, self.root.images['logo'])

        self._vbar = ttk.Scrollbar(self._win, orient=tk.VERTICAL)
        self._tree = ttk.Treeview(self._win, columns=('complete', 'type', 'params'), show='tree', displaycolumns=(), height=10, selectmode='browse',
                                  yscrollcommand=self._vbar.set)
        self._vbar.config(command=self._tree.yview)
        self._vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._win.bind('<Escape>', lambda f: self._win.destroy())
        self._tree.bind('<Double-1>', self._complete)
        self._tree.bind('<Return>', self._complete)

        for c in completions:
            try:
                params = []
                for p in c.params:
                    params.append(p.name)
                params = ','.join(params)
                self._tree.insert('', 'end', text=c.name, values=(c.complete, c.type, params))
            except (AttributeError, NotImplementedError):
                self._tree.insert('', 'end', text=c.name, values=(c.complete, c.type, ''))

        self._tree.focus(self._tree.get_children()[0])
        self._tree.focus_set()

    def show_completion(self, tab):
        """Method shows code completion window

        Args:
            tab (obj): tab reference

        Returns:
            void

        """

        if (self._win is not None):
            self._win.destroy()

        suffix = tab.path.split('.')[-1]
        if (suffix in ['py', 'jedi', 'padawan']):
            self._tab = tab
            row, col = tab.text.index(tk.INSERT).split('.')

            try:
                script = Script(tab.text.get('1.0', 'end-1c'), int(row), int(col))
                completions = script.completions()
            except ValueError:
                return

            cnt = len(completions)
            if (cnt == 0):
                return

            if (cnt == 1):
                self._complete(completion=completions[0])
            else:
                self._set_gui(completions)

    def _complete(self, event=None, completion=None):
        """Method completes code

        Args:
            event (obj): event
            completion (obj): code completion

        Returns:
            void

        """

        if (completion == None):
            item = self._tree.selection()
            if (len(item) == 0):
                return

            complete, item_type, params = self._tree.item(item)['values']
            self._win.destroy()
        else:
            complete, item_type = completion.complete, completion.type
            try:
                params = []
                for p in completion.params:
                    params.append(p.name)
                params = ','.join(params)
            except (AttributeError, NotImplementedError):
                params = False

        if (item_type in ['function', 'class']):
            if (params):
                complete += '('
                for p in params.split(','):
                    complete += '%s=%s, ' % (p, p)
                complete = complete[:-2] + ')'
            else:
                complete += '()'

        self.tab.disable_format()
        self.tab.text.insert(tk.INSERT, complete)
