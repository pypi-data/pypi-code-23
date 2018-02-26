# -*- coding: utf-8 -*-
"""Editor frame

.. module:: client.core.editor
   :platform: Windows, Unix
   :synopsis: Editor frame
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

import os

from hydratk.extensions.client.core.tkimport import tk, ttk, tkmsg, tkfd
from hydratk.extensions.client.core.notebook import CustomNotebook
from hydratk.extensions.client.core.utils import fix_path

class Editor(tk.LabelFrame):
    """Class Explorer
    """

    _instance = None
    _instance_created = False

    # references
    _root = None
    _trn = None
    _config = None
    _logger = None
    _explorer = None
    _yoda_tree = None

    # gui elements
    _nb = None
    _var_show_line_number = None
    _var_show_info_bar = None

    # font
    _font = None

    def __init__(self, root):
        """Class constructor

        Called when object is initialized

        Args:
           root (obj): root frame

        Raises:
           error: ValueError

        """

        if (self._instance_created == False):
            raise ValueError('For creating class instance please use the get_instance method instead!')
        if (self._instance is not None):
            raise ValueError('A Class instance already exists, use get_instance method instead!')

        self._root = root
        self._trn = self.root.trn
        self._config = self.root.cfg

        tk.LabelFrame.__init__(self, self.root._pane_right, text=self.trn.msg('htk_gui_editor_label'))
        self._set_gui()
        self._parse_config()

    @staticmethod
    def get_instance(root=None):
        """Method gets Explorer singleton instance

        Args:
            root (obj): root frame

        Returns:
            obj

        """

        if (Editor._instance is None):
            Editor._instance_created = True
            Editor._instance = Editor(root)

        return Editor._instance

    @property
    def root(self):
        """ root property getter """

        return self._root

    @property
    def trn(self):
        """ trn property getter """

        return self._trn

    @property
    def config(self):
        """ config property getter """

        return self._config

    @property
    def logger(self):
        """ logger property getter """

        if (self._logger is None):
            self._logger = self.root.logger

        return self._logger

    @property
    def explorer(self):
        """ explorer property getter """

        if (self._explorer is None):
            self._explorer = self.root.explorer

        return self._explorer

    @property
    def yoda_tree(self):
        """ yoda_tree property getter """

        if (self._yoda_tree is None):
            self._yoda_tree = self.root.yoda_tree

        return self._yoda_tree

    @property
    def nb(self):
        """ nb property getter """

        return self._nb

    @property
    def var_show_line_number(self):
        """ var_show_line_number property getter """

        return self._var_show_line_number

    @property
    def var_show_info_bar(self):
        """ var_show_info_bar property getter """

        return self._var_show_info_bar

    @property
    def font(self):
        """ font property getter """

        return self._font

    def _parse_config(self):
        """Method parses configuration

        Args:
            none

        Returns:
            void

        """

        cfg = self.config.data['Core']['editor']
        self._var_show_line_number = tk.BooleanVar(value=True) if (cfg['view']['show_line_number'] == 1) else tk.BooleanVar(value=False)
        self._var_show_info_bar = tk.BooleanVar(value=True) if (cfg['view']['show_info_bar'] == 1) else tk.BooleanVar(value=False)

        self._font = {
                      'family' : cfg['font']['family'],
                      'size'   : cfg['font']['size'],
                      'style'  : cfg['font']['style']
                     }

    def _set_gui(self):
        """Method sets graphical interface

        Args:
            none

        Returns:
            void

        """

        self._nb = CustomNotebook(self, height=650)
        self._nb.pack(expand=True, fill=tk.BOTH, padx=2, pady=3)

    def new_file(self, event=None):
        """Method opens new file tab

        Args:
            event (obj): event

        Returns:
            void

        """

        self.nb._new_cnt += 1
        tab_text = '{0}_{1}.txt'.format(self.trn.msg('htk_gui_editor_tab_new_text'), self.nb.new_cnt)
        self.nb.add_tab(text=tab_text)
        
    def open_file(self, event=None, path=None):
        """Method opens file

        File is opened from dialog or path, the content is displayed in tab

        Args:
            event (obj): event
            path (str): file path

        Returns:
            void

        """

        if (path is None):
            path = tkfd.askopenfilename(filetypes=[(self.trn.msg('htk_gui_editor_filetypes'), '*.*')])
            if (len(path) == 0):
                return

        path = fix_path(path)
        name = os.path.split(path)[1]
        res, idx = self.nb.is_tab_present(path)
        if (not res):
            with open(path, 'r') as f:
                content = f.read()
                self.nb.add_tab(path=path, content=content, text=name)
                self.yoda_tree.add_test(path, content)
                self.logger.debug(self.trn.msg('htk_core_file_opened', path))
        else:
            self.nb.select(idx)

    def save_as_file(self, event=None):
        """Method saves new file as

        Choose file name in dialog, content is stored to file

        Args:
            event (obj): event

        Returns:
            void

        """

        path = tkfd.asksaveasfilename(filetypes=[(self.trn.msg('htk_gui_editor_filetypes'), '*.*')])
        if (len(path) == 0):
            return

        with open(path, 'w') as f:
            content = self.nb.get_current_content()
            f.write(content)
            self.logger.debug(self.trn.msg('htk_core_file_saved', path))
            name = os.path.split(path)[1]
            self.nb.set_current_tab(name, path, False)
            self.explorer.refresh(path=path)
            self.yoda_tree.add_test(path, content)
            
    def save_file(self, event=None, path=None, idx=None):
        """Method saves file

        From current tab, file path or requested tab

        Args:
            event (obj): event
            path (str): file path
            idx (int): tab index

        Returns:
            void

        """

        tab = self.nb.get_current_tab()
        if (tab is not None):
            if (path is None):
                path = tab.path
            if (path is None):
                self.save_as_file()
            else:
                with open(path, 'w') as f:
                    content = self.nb.get_current_content() if (idx is None) else self._nb.get_content(idx)
                    f.write(content)
                    self.logger.debug(self.trn.msg('htk_core_file_saved', path))
                    tab.text.edit_modified(False)

    def undo(self, event=None):
        """Method undos last text change

        Args:
            event (obj): event

        Returns:
            void

        """

        try:
            tab = self.nb.get_current_tab()
            if (tab is not None):
                tab.text.edit_undo()
                tab.update_line_numbers()
                tab.colorize()
                return 'break'
        except tk.TclError:
            pass

    def redo(self, event=None):
        """Method redos next text change

        Args:
            event (obj): event

        Returns:
            void

        """

        try:
            tab = self.nb.get_current_tab()
            if (tab is not None):
                tab.text.edit_redo()
                tab.update_line_numbers()
                tab.colorize()
                return 'break'
        except tk.TclError:
            pass

    def cut(self, event=None):
        """Method cuts marked text and stores it in clipboard

        Args:
            event (obj): event

        Returns:
            void

        """

        content = self.nb.get_marked_content()
        if (content is not None):
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            tab = self.nb.get_current_tab()
            tab.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            tab.update_line_numbers()
            self.refresh_yoda_tree()

    def copy(self, event=None):
        """Method copies marked text and stores it in clipboard

        Args:
            event (obj): event

        Returns:
            void

        """

        content = self.nb.get_marked_content()
        if (content is not None):
            self.root.clipboard_clear()
            self.root.clipboard_append(content)

    def paste(self, event=None):
        """Method pastes text from clipboard

        Args:
            event (obj): event

        Returns:
            void

        """

        tab = self.nb.get_current_tab()
        if (tab is not None):
            content = self.root.clipboard_get()
            start = tab.text.index(tk.INSERT)
            stop = '{0}+{1}c'.format(start, len(content))
            tab.text.insert(tk.INSERT, content)
            tab.update_line_numbers()
            tab.colorize(start, stop)
            return 'break'

    def delete(self, event=None):
        """Method deletes marked text

        Args:
            event (obj): event

        Returns:
            void

        """

        content = self.nb.get_marked_content()
        if (content is not None):
            tab = self.nb.get_current_tab()
            tab.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            tab.update_line_numbers()
            self.refresh_yoda_tree()

    def select_all(self, event=None):
        """Method marks tab text content

        Args:
            event (obj): event

        Returns:
            void

        """

        tab = self.nb.get_current_tab()
        if (tab is not None):
            tab.text.tag_add(tk.SEL, '1.0', 'end')

    def save_tabs(self):
        """Method saves all tab content

        Dialog is displayed for new files

        Args:
            event (obj): event

        Returns:
            void

        """

        for i in range(0, len(self.nb.tab_refs)):
            tab = self.nb.tab_refs[i]
            if (tab.text.edit_modified()):
                res = tkmsg.askyesno(self.trn.msg('htk_gui_editor_close_save_title'),
                                     self.trn.msg('htk_gui_editor_close_save_question', tab.name))
                if (res):
                    self.save_file(path=tab.path, idx=i)

    def show_line_number(self, event=None):
        """Method enables/disables showing of line numbers

        Args:
            event (obj): event

        Returns:
            void

        """

        for tab in self.nb.tab_refs:
            tab.update_line_numbers()

        self.config.data['Core']['editor']['view']['show_line_number'] = 1 if (self._var_show_line_number.get()) else 0

    def show_info_bar(self, event=None):
        """Method enables/disables showing of info bar

        Args:
            event (obj): event

        Returns:
            void

        """
        
        for tab in self.nb.tab_refs:
            tab.update_info_bar()

        self.config.data['Core']['editor']['view']['show_info_bar'] = 1 if (self._var_show_info_bar.get()) else 0
        
    def win_goto(self, event=None):
        """Method displays Goto window

        Args:
            event (obj): event

        Returns:
            void

        """

        tab = self.nb.get_current_tab()
        if (tab is not None):
            win = tk.Toplevel(self.root)
            win.title(self.trn.msg('htk_gui_editor_goto_title'))
            win.transient(self.root)
            win.resizable(False, False)
            win.geometry('+%d+%d' % (self.root.winfo_screenwidth() / 2, self.root.winfo_screenheight() / 2))
            win.tk.call('wm', 'iconphoto', win._w, self.root.images['logo'])

            tk.Label(win, text=self.trn.msg('htk_gui_editor_goto_text')).pack(side=tk.LEFT, padx=3)
            entry = tk.Entry(win, width=15)
            entry.pack(side=tk.LEFT, padx=3)
            entry.focus_set()
            btn = tk.Button(win, text='OK', command=lambda: self._goto(entry.get(), win))
            btn.pack(side=tk.LEFT, padx=3)

            win.bind('<Escape>', lambda f: win.destroy())

    def _goto(self, line, win=None):
        """Method goes to given line

        Args:
            line (int): line number
            win (obj): window reference

        Returns:
            void

        """

        if (len(line) > 0):
            tab = self.nb.get_current_tab()
            tab.goto(line)

        if (win is not None):
            win.destroy()

    def win_find(self, event=None):
        """Method displays Find window

        Args:
            event (obj): event

        Returns:
            void

        """

        tab = self.nb.get_current_tab()
        if (tab is not None):
            win = tk.Toplevel(self.root)
            win.title(self.trn.msg('htk_gui_editor_find_title'))
            win.transient(self.root)
            win.resizable(False, False)
            win.geometry('+%d+%d' % (self.root.winfo_screenwidth() / 2, self.root.winfo_screenheight() / 2))
            win.tk.call('wm', 'iconphoto', win._w, self.root.images['logo'])

            tk.Label(win, text=self.trn.msg('htk_gui_editor_find_text')).grid(row=0, column=0, sticky='e')
            entry = tk.Entry(win, width=50)
            entry.grid(row=0, column=1, padx=3, sticky='e')
            entry.focus_set()

            find_all = tk.BooleanVar(value=True)
            tk.Checkbutton(win, text=self.trn.msg('htk_gui_editor_find_find_all'), variable=find_all).grid(row=1, column=1, pady=3, sticky='w')
            ignore_case = tk.BooleanVar(value=True)
            tk.Checkbutton(win, text=self.trn.msg('htk_gui_editor_find_ignore_case'), variable=ignore_case).grid(row=2, column=1, sticky='w')
            regexp = tk.BooleanVar()
            tk.Checkbutton(win, text=self.trn.msg('htk_gui_editor_find_regexp'), variable=regexp).grid(row=3, column=1, sticky='w')

            btn = tk.Button(win, text='OK', command=lambda: self._find(entry.get(), find_all.get(), ignore_case.get(), regexp.get(), win))
            btn.grid(row=0, column=2, padx=3, sticky='e')

            win.bind('<Escape>', lambda f: win.destroy())

    def _find(self, find_str, find_all, ignore_case, regexp, win=None):
        """Method finds given string and highlights it

        Args:
            find_str (str): string to find
            find_all (bool): find all occurrences, otherwise only next one
            ignore_case (bool): ignore case
            regexp (bool): regular expression
            win (obj): window reference

        Returns:
            void

        """

        if (len(find_str) > 0):
            tab = self.nb.get_current_tab()
            tab.find(find_str=find_str, find_all=find_all, ignore_case=ignore_case, regexp=regexp)

        if (win is not None):
            win.destroy()

    def win_replace(self, event=None):
        """Method displays Replace window

        Args:
            event (obj): event

        Returns:
            void

        """

        tab = self.nb.get_current_tab()
        if (tab is not None):
            win = tk.Toplevel(self.root)
            win.title(self.trn.msg('htk_gui_editor_replace_title'))
            win.transient(self.root)
            win.resizable(False, False)
            win.geometry('+%d+%d' % (self.root.winfo_screenwidth() / 2, self.root.winfo_screenheight() / 2))
            win.tk.call('wm', 'iconphoto', win._w, self.root.images['logo'])

            tk.Label(win, text=self.trn.msg('htk_gui_editor_replace_find')).grid(row=0, column=0, sticky='e')
            find_entry = tk.Entry(win, width=50)
            find_entry.grid(row=0, column=1, padx=3, sticky='e')
            find_entry.focus_set()

            tk.Label(win, text=self.trn.msg('htk_gui_editor_replace_replace')).grid(row=1, column=0, pady=3, sticky='e')
            replace_entry = tk.Entry(win, width=50)
            replace_entry.grid(row=1, column=1, padx=3, sticky='e')

            replace_all = tk.BooleanVar(value=True)
            tk.Checkbutton(win, text=self.trn.msg('htk_gui_editor_replace_replace_all'), variable=replace_all).grid(row=2, column=1, pady=3, sticky='w')
            ignore_case = tk.BooleanVar(value=True)
            tk.Checkbutton(win, text=self.trn.msg('htk_gui_editor_replace_ignore_case'), variable=ignore_case).grid(row=3, column=1, sticky='w')
            regexp = tk.BooleanVar()
            tk.Checkbutton(win, text=self.trn.msg('htk_gui_editor_replace_regexp'), variable=regexp).grid(row=4, column=1, sticky='w')

            btn = tk.Button(win, text='OK', command=lambda: self._replace(find_entry.get(), replace_entry.get(), replace_all.get(), ignore_case.get(), regexp.get(), win))
            btn.grid(row=0, column=2, padx=3, sticky='e')

            win.bind('<Escape>', lambda f: win.destroy())
            
    def _replace(self, find_str, replace_str, replace_all, ignore_case, regexp, win=None):
        """Method finds given string and replaces it

        Args:
            find_str (str): string to find
            replace_str (str): string to replace
            replace_all (bool): replace all occurrences, otherwise only next one
            ignore_case (bool): ignore case
            regexp (bool): regular expression
            win (obj): window reference

        Returns:
            void

        """

        if (len(find_str) > 0):
            tab = self.nb.get_current_tab()
            tab.replace(find_str, replace_str, replace_all, ignore_case, regexp)
            self.refresh_yoda_tree(tab)

        if (win is not None):
            win.destroy()

    def increase_font(self):
        """Method increases font size

        Args:
            none

        Returns:
            void

        """
        
        if (self._font['size'] < 50):
            self._font['size'] += 1
            for tab in self.nb.tab_refs:
                tab.set_font(self._font['family'], self._font['size'], self._font['style'])
        
    def decrease_font(self):
        """Method decreases font size

        Args:
            none

        Returns:
            void

        """

        if (self._font['size'] > 1.0):
            self._font['size'] -= 1
            for tab in self.nb.tab_refs:
                tab.set_font(self._font['family'], self._font['size'], self._font['style'])

    def on_tab_changed(self, event=None):
        """Method handles tab changed event

        Args:
            event (obj): event

        Returns:
            void

        """

        tab = self.nb.get_current_tab()
        if (tab != None):
            self.yoda_tree.add_test(tab.path)
        else:
            self.yoda_tree.clear_tree()

    def refresh_yoda_tree(self, tab=None):
        """Method refreshes yoda tree

        Args:
            tab (obj): tab

        Returns:
            void

        """
        
        if (tab == None):
            tab = self.nb.get_current_tab()
        self.yoda_tree.refresh(tab.path, tab.text.get('1.0', 'end-1c'))
