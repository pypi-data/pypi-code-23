# -*- coding: utf-8 -*-
"""Project explorer frame

.. module:: client.core.explorer
   :platform: Windows, Unix
   :synopsis: Project explorer frame
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

import os
from shutil import rmtree, copy

from hydratk.extensions.client.core.tkimport import tk, ttk, tkmsg, tkfd
from hydratk.extensions.client.core.autocompleter import AutoCompleter
from hydratk.extensions.client.core.utils import fix_path
import hydratk.extensions.client.core.template as tmpl

class Explorer(tk.LabelFrame):
    """Class Explorer
    """
    
    _instance = None
    _instance_created = False

    # references
    _root = None
    _trn = None
    _config = None
    _editor = None
    _logger = None
    _yoda_tree = None
    _autocompleter = None

    # project parameters
    _projects = None
    _show_hidden = None
    
    # gui elements
    _tree = None
    _vsb = None
    _hsb = None

    _menu = None
    _menu_new = None

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

        tk.LabelFrame.__init__(self, self.root.pane_left, text=self.trn.msg('htk_gui_explorer_label'))
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

        if (Explorer._instance is None):
            Explorer._instance_created = True
            Explorer._instance = Explorer(root)

        return Explorer._instance

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
    def editor(self):
        """ editor property getter """

        if (self._editor is None):
            self._editor = self.root.editor

        return self._editor

    @property
    def logger(self):
        """ logger property getter """

        if (self._logger is None):
            self._logger = self.root.logger

        return self._logger

    @property
    def yoda_tree(self):
        """ yoda_tree property getter """

        if (self._yoda_tree is None):
            self._yoda_tree = self.root.yoda_tree

        return self._yoda_tree

    @property
    def autocompleter(self):
        """ autocompleter property getter """

        if (self._autocompleter is None):
            self._autocompleter = AutoCompleter.get_instance()

        return self._autocompleter

    def _parse_config(self):
        """Method parses configuration

        Args:
            none

        Returns:
            void

        """

        self._projects = self.config.data['Projects'] if ('Projects' in self.config.data and self.config.data['Projects'] != None) else {}
        self._show_hidden = self.config.data['Core']['explorer']['show_hidden']

        for name, cfg in self._projects.items():
            self._populate_project(name, cfg)

    def _set_gui(self):
        """Method sets graphical interface

        Args:
            none

        Returns:
            void

        """

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # treeview
        self._tree = ttk.Treeview(self, columns=('path', 'type'), show='tree', displaycolumns=(), height=20, selectmode='browse',
                                  xscrollcommand=lambda f, l: self._autoscroll(self._hsb, f, l),
                                  yscrollcommand=lambda f, l: self._autoscroll(self._vsb, f, l))
        self._tree.grid(in_=self, row=0, column=0, sticky=tk.NSEW)

        # scrollbars
        self._vsb = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._tree.yview)
        self._vsb.grid(in_=self, row=0, column=1, sticky=tk.NS)
        self._hsb = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self._tree.xview)
        self._hsb.grid(in_=self, row=1, column=0, sticky=tk.EW)

        self._tree['yscroll'] = self._vsb.set
        self._tree['xscroll'] = self._hsb.set
        self._tree.heading('#0', text='File', anchor='w')
        self._tree.column('#0', stretch=True, minwidth=300, width=250)

        # events
        self._tree.bind('<<TreeviewOpen>>', self._update_tree)
        self._tree.bind('<Double-1>', self._open)
        self._tree.bind('<Control-c>', self._copy)
        self._tree.bind('<Control-v>', self._paste)
        self._tree.bind('<Delete>', self._delete)
        self._tree.bind('<F5>', self.refresh)

        self._set_menu()

    def _set_menu(self):
        """Method sets menu

        Args:
            none

        Returns:
            void

        """

        self._menu = tk.Menu(self._tree, tearoff=False)
        self._menu_new = tk.Menu(self._menu, tearoff=False)
        self._menu.add_cascade(label=self.trn.msg('htk_gui_explorer_menu_new'), menu=self._menu_new)
        self._menu_new.add_command(label=self.trn.msg('htk_gui_explorer_menu_new_file'), accelerator='Ctrl+N', command=self.new_file)
        self._menu_new.add_command(label=self.trn.msg('htk_gui_explorer_menu_new_directory'), command=self.new_directory)
        self._menu_new.add_command(label=self.trn.msg('htk_gui_explorer_menu_new_project'), command=self.new_project)
        self._menu_new.add_command(label=self.trn.msg('htk_gui_explorer_menu_new_helper'), command=self.new_helper)
        self._menu_new.add_command(label=self.trn.msg('htk_gui_explorer_menu_new_library'), command=self.new_library)
        self._menu_new.add_command(label=self.trn.msg('htk_gui_explorer_menu_new_test'), command=self.new_test)
        self._menu_new.add_command(label=self.trn.msg('htk_gui_explorer_menu_new_archive'), command=self.new_archive)
        self._menu_new.add_command(label=self.trn.msg('htk_gui_explorer_menu_new_draft'), command=self.new_draft)

        self._menu.add_command(label=self.trn.msg('htk_gui_explorer_menu_open'), accelerator='Ctrl+O', command=self._open)
        self._menu.add_command(label=self.trn.msg('htk_gui_explorer_menu_copy'), accelerator='Ctrl+C', command=self._copy)
        self._menu.add_command(label=self.trn.msg('htk_gui_explorer_menu_paste'), accelerator='Ctrl+V', command=self._paste)
        self._menu.add_command(label=self.trn.msg('htk_gui_explorer_menu_delete'), accelerato='Delete', command=self._delete)
        self._menu.add_command(label=self.trn.msg('htk_gui_explorer_menu_refresh'), accelerator='F5', command=self.refresh)

        self._tree.bind('<Button-3>', self._context_menu)

    def _autoscroll(self, sbar, idx1, idx2):
        """Method for automatic treeview scroll

        Args:
            sbar (obj): scrollbar
            idx1 (int): start index
            idx2 (int): stop index

        Returns:
            void

        """

        idx1, idx2 = float(idx1), float(idx2)
        if (idx1 <= 0 and idx2 >= 1):
            sbar.grid_remove()
        else:
            sbar.grid()
        sbar.set(idx1, idx2)

    def _context_menu(self, event=None):
        """Method sets context menu

        Args:
            event (obj): event

        Returns:
            void

        """

        self._menu.tk_popup(event.x_root, event.y_root)

    def _populate_project(self, name, cfg):
        """Method populates given project

        Args:
            name (str): project name
            cfg (dict): project configuration

        Returns:
            void

        """
        
        if (os.path.exists(cfg['path'])):
            node = self._tree.insert('', 'end', text=name, values=(cfg['path'], 'directory'))
            self._populate_tree(node)
        else:
            del self._projects[name]

    def _populate_tree(self, node):
        """Method populates project tree

        It displays directory and file name, path is hidden
        Directory is can be expanded/collapsed

        Args:
            node (obj): tree node

        Returns:
            void

        """
        
        if self._tree.set(node, 'type') != 'directory':
            return

        path = self._tree.set(node, 'path')
        if (len(path) == 0):
            return

        self._tree.delete(*self._tree.get_children(node))

        if (os.path.exists(path)):
            for p in os.listdir(path):
                ptype = None
                p = os.path.join(path, p)
                if (os.path.isdir(p)):
                    ptype = 'directory'
                elif (os.path.isfile(p)):
                    ptype = 'file'

                fname = os.path.split(p)[1]
                if (self._show_hidden or fname[0] != '.'):
                    id = self._tree.insert(node, 'end', text=fname, values=(fix_path(p), ptype))

                    if (ptype == 'directory'):
                        self._tree.insert(id, 'end')
                        self._tree.item(id, text=fname)
                    elif (ptype == 'file'):
                        self._tree.set(id)
        else:
            self.refresh(path)

    def _update_tree(self, event=None):
        """Method updates tree

        Args:
            event (obj): event

        Returns:
            void

        """

        self._tree = event.widget
        self._populate_tree(self._tree.focus())

    def new_file(self):
        """Method creates new file

        Args:
            none

        Returns:
            void

        """

        self.editor.new_file()

    def new_project(self):
        """Method creates new project

        File dialog is displayed, choose existing directory or create new one
        Windows: create directory via dialog
        Linux: append path with directory name
        Project is stored to configuration

        Args:
            none

        Returns:
            void

        """
        
        dirpath = tkfd.askdirectory()
        proj_name = os.path.split(dirpath)[1]
        if (len(proj_name) == 0 or proj_name in self._projects):
            return

        if (not os.path.exists(dirpath)):
            os.makedirs(dirpath)

        # initial directory structure
        if (len(os.listdir(dirpath)) == 0):
            for d in tmpl.proj_dir_struct:
                os.makedirs(d.format(proj_root=dirpath))
                
            for f in tmpl.proj_files:
                with open(f.format(proj_root=dirpath), 'w') as fl:
                    fl.write(tmpl.init_content)

        self._projects[proj_name] = {'path': dirpath, 'pythonpath': [dirpath + '/lib/yodalib', dirpath + '/helpers/yodahelpers']}
        node = self._tree.insert('', 'end', text=proj_name, values=(dirpath, 'directory'))
        self._populate_tree(node)
        self.logger.info(self.trn.msg('htk_core_project_created', proj_name))
        self.config.data['Projects'] = self._projects
        self.autocompleter.update_pythonpath()
        self.config.save()
        
    def new_directory(self):
        """Method creates new directory

        File dialog is displayed
        Windows: create directory via dialog
        Linux: append path with directory name

        Args:
            none

        Returns:
            void

        """

        item = self._tree.selection()
        initialdir = None
        if (len(item) > 0):
            item = self._tree.item(item)
            initialdir = item['values'][0] if (item['values'][1] == 'directory') else os.path.split(item['values'][0])[0]

        path = tkfd.askdirectory(initialdir=initialdir)
        if (len(path) == 0):
            return

        if (not os.path.exists(path)):
            os.makedirs(path)
        self.logger.debug(self.trn.msg('htk_core_directory_created', path))
        self.refresh(path=path)

    def _new_template_file(self, filetype, extension, template, langtext):
        """Method creates new file from template

        Args:
            filetype (str): filetype displayed in dialog
            extension (str): file extension
            template (str): content template
            langtext (str): langtext for logger

        Returns:
            void

        """

        item = self._tree.selection()
        initialdir = None
        if (len(item) > 0):
            item = self._tree.item(item)
            initialdir = item['values'][0] if (item['values'][1] == 'directory') else os.path.split(item['values'][0])[0]

        path = tkfd.asksaveasfilename(initialdir=initialdir, filetypes=[(filetype, '*' + extension)])
        if (len(path) == 0):
            return

        path = fix_path(path)
        if (extension not in path):
            path += extension

        name = os.path.split(path)[1]
        content = template.format(name=name.split('.')[0], path=name)
        with open(path, 'w') as f:
            f.write(content)

        self.editor.nb.add_tab(path=path, content=content, text=name)
        self.yoda_tree.add_test(path, content)
        self.logger.debug(self.trn.msg(langtext, path))
        self.refresh(path=path)

    def new_helper(self):
        """Method creates new helper

        Args:
            none

        Returns:
            void

        """

        self._new_template_file('Python', '.py', tmpl.helper_content, 'htk_core_helper_created')

    def new_library(self):
        """Method creates new library

        Args:
            none

        Returns:
            void

        """

        self._new_template_file('Python', '.py', tmpl.library_content, 'htk_core_library_created')

    def new_test(self):
        """Method creates new test

        Args:
            none

        Returns:
            void

        """

        self._new_template_file('Jedi', '.jedi', tmpl.test_content, 'htk_core_test_created')

    def new_archive(self):
        """Method creates new archive

        Args:
            none

        Returns:
            void

        """

        self._new_template_file('Yoda', '.yoda', tmpl.archive_content, 'htk_core_archive_created')

    def new_draft(self):
        """Method creates new draft

        Args:
            none

        Returns:
            void

        """

        self._new_template_file('Padawan', '.padawan', tmpl.draft_content, 'htk_core_draft_created')

    def _open(self, event=None):
        """Method opens file from explorer tree

        Args:
            event (obj): event

        Returns:
            void

        """
        
        item = self._tree.selection()
        if (len(item) == 0):
            return

        item = self._tree.item(item)
        if (item['values'][1] == 'file'):
            self.editor.open_file(path=item['values'][0])
            
    def _copy(self, event=None):
        """Method copies file from explorer tree

        Args:
            event (obj): event

        Returns:
            void

        """

        item = self._tree.selection()
        if (len(item) == 0):
            return

        item = self._tree.item(item)
        self.root.clipboard_clear()
        self.root.clipboard_append(item['values'][0])

    def _paste(self, event=None):
        """Method pastes file from explorer tree

        Args:
            event (obj): event

        Returns:
            void

        """

        item = self._tree.selection()
        if (len(item) == 0):
            return

        item = self._tree.item(item)
        path, item_type = item['values']
        if (item_type == 'directory'):
            src = self.root.clipboard_get()
            if (os.path.isfile(src)):
                copy(src, path)
                self.logger.debug(self.trn.msg('htk_core_copied', src, path))
                self.refresh(path=path)

    def _delete(self, event=None):
        """Method deletes file or directory from explorer tree

        Deletion must be confirmed via popup window
        Deleted project is removed from configuration

        Args:
            event (obj): event

        Returns:
            void

        """

        item = self._tree.selection()
        if (len(item) == 0):
            return

        item = self._tree.item(item)
        path, item_type = item['values']
        path = fix_path(path)
        if (item_type == 'file'):
            question = 'htk_gui_explorer_delete_file'
        else:
            is_project, i = False, 0
            for name, cfg in self._projects.items():
                if (cfg['path'] == path):
                    is_project, proj_name = True, name
                    break
                i += 1
            question = 'htk_gui_explorer_delete_project' if (is_project) else 'htk_gui_explorer_delete_directory'
        
        res = tkmsg.askyesno(self.trn.msg('htk_gui_explorer_delete'), self.trn.msg(question, path))
        if (res):
            if (item_type == 'file'):
                os.remove(path)
                self.logger.debug(self.trn.msg('htk_core_file_deleted', path))
                self.refresh(path)

                res, index = self.editor.nb.is_tab_present(path)
                if (res):
                    self.editor.nb.close_tab(index=index)
                    
            else:
                rmtree(path)
                if (is_project):
                    self.logger.info(self.trn.msg('htk_core_project_deleted', proj_name))
                    self._tree.delete(self._tree.get_children()[i])
                    del self._projects[proj_name]
                    self.config.data['Projects'] = self._projects
                    self.config.save()
                else:
                    self.logger.debug(self.trn.msg('htk_core_directory_deleted', path))
                    self.refresh(path)

    def refresh(self, event=None, path=None):
        """Method refreshes explorer tree if content is changed

        Args:
            event (obj): event
            path (str): directory of file path

        Returns:
            void

        """

        if (path is None):
            item = self._tree.selection()
            if (len(item) == 0):
                return
            path = self._tree.item(item)['values'][0]

        i = 0
        path = fix_path(path)
        for name, cfg in self._projects.items():
            if (cfg['path'] + '/' in path or cfg['path'] == path):
                node = self._tree.get_children()[i]
                self._populate_tree(node)
                break
            i += 1
