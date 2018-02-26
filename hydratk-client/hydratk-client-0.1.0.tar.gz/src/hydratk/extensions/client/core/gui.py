# -*- coding: utf-8 -*-
"""Main GUI frame

.. module:: client.core.gui
   :platform: Windows, Unix
   :synopsis: Main GUI frame
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

import traceback
from os import path

from hydratk.extensions.client.core.tkimport import tk, tkmsg, c_os
from hydratk.extensions.client.core.config import Config
from hydratk.extensions.client.core.translator import Translator
from hydratk.extensions.client.core.explorer import Explorer
from hydratk.extensions.client.core.yoda_tree import YodaTree
from hydratk.extensions.client.core.editor import Editor
from hydratk.extensions.client.core.logger import Logger
from hydratk.extensions.client.core.pluginmanager import PluginManager
from hydratk.extensions.client.core.help import Help
from hydratk.extensions.client.core.tooltip import ToolTip

class Gui(tk.Tk):
    """Class Gui
    """

    _instance = None
    _instance_created = False

    # references
    _config = None
    _trn = None
    _explorer = None
    _yoda_tree = None
    _editor = None
    _logger = None
    _pluginmanager = None
    _plugins = {}
    _help = None

    # frames
    _frame_main = None
    _pane_main = None
    _pane_left = None
    _pane_right = None

    # menu
    _menu_bar = None
    _menus = {}

    # toolbar
    _tool_bar = None
    _tools = {}
    _tooltips = {}
    _images = {}
    _imgdir = None

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

        tk.CallWrapper = ExceptionHandler
        self._config = Config.get_instance()
        self._trn = Translator.get_instance(self._config._data['Core']['language'])

        self._instance = tk.Tk.__init__(self)
        self._set_gui()

    @staticmethod
    def get_instance():
        """Method gets Gui singleton instance

        Args:
            none

        Returns:
            obj

        """

        if (Gui._instance is None):
            Gui._instance_created = True
            Gui._instance = Gui()

        return Gui._instance

    @property
    def cfg(self):
        """ config property getter """

        return self._config

    @property
    def trn(self):
        """ trn property getter """

        return self._trn

    @property
    def explorer(self):
        """ explorer property getter """

        return self._explorer

    @property
    def yoda_tree(self):
        """ yoda_tree property getter """

        return self._yoda_tree

    @property
    def editor(self):
        """ editor property getter """

        return self._editor

    @property
    def logger(self):
        """ logger property getter """

        return self._logger

    @property
    def pluginmanager(self):
        """ pluginmanager property getter """

        return self._pluginmanager

    @property
    def plugins(self):
        """ plugins property getter """

        return self._plugins

    @property
    def help(self):
        """ help property getter """

        return self._help

    @property
    def menu_bar(self):
        """ menu_bar property getter """

        return self._menu_bar

    @property
    def menus(self):
        """ menus property getter """

        return self._menus

    @property
    def tools(self):
        """ tools property getter """

        return self._tools

    @property
    def imgdir(self):
        """ imgdir property getter """

        return self._imgdir

    @property
    def images(self):
        """ images property getter """

        return self._images

    @property
    def pane_left(self):
        """ pane_left property getter """

        return self._pane_left

    @property
    def pane_right(self):
        """ pane_right property getter """

        return self._pane_right

    def _set_gui(self):
        """Method sets graphical interface

        Args:
            none

        Returns:
            void

        """

        self._set_window()
        self._set_pane_left()
        self._set_pane_right()
        self._set_menu()
        self._set_toolbar()
        self._load_plugins()

        self.logger.info(self.trn.msg('htk_core_started'))

    def _set_window(self):
        """Method sets window

        Args:
            none

        Returns:
            void

        """

        self.title('HydraTK')
        self._imgdir = path.join(path.dirname(path.dirname(__file__)), 'img')
        self._images['logo'] = tk.PhotoImage(file=path.join(self._imgdir, 'logo.gif'))
        self.tk.call('wm', 'iconphoto', self._w, self._images['logo'])
        if (c_os == 'Windows'):
            self.wm_state('zoomed')
        else:
            self.wm_attributes('-zoomed', True)
        self.protocol('WM_DELETE_WINDOW', self._exit)

        self._menu_bar = tk.Menu(self)
        self.config(menu=self._menu_bar)

        self._tool_bar = tk.Frame(self)
        self._tool_bar.pack(expand=False, fill=tk.X)

        self._frame_main = tk.Frame(self)
        self._frame_main.pack(expand=True, fill=tk.BOTH)
        self._pane_main = tk.PanedWindow(self._frame_main, orient=tk.HORIZONTAL, sashwidth=10)
        self._pane_main.pack(expand=True, fill=tk.BOTH, padx=10, pady=(6, 10))

    def _set_menu(self):
        """Method sets main menu

        Args:
            none

        Returns:
            void

        """

        self._set_menu_file()
        self._set_menu_edit()
        self._set_menu_view()
        self._set_menu_plugin()
        self._set_menu_help()

    def _set_menu_file(self):
        """Method sets file menu

        Args:
            none

        Returns:
            void

        """

        menu_file = tk.Menu(self._menu_bar, tearoff=False)
        self._menus['file'] = menu_file
        self._menu_bar.add_cascade(label=self.trn.msg('htk_gui_menu_file'), menu=menu_file)

        # submenu new
        menu_file_new = tk.Menu(menu_file, tearoff=False)
        self._menus['file_new'] = menu_file_new
        menu_file.add_cascade(label=self.trn.msg('htk_gui_menu_file_new'), menu=menu_file_new)
        menu_file_new.add_command(label=self.trn.msg('htk_gui_menu_file_new_file'), accelerator='Ctrl+N', command=self.editor.new_file)
        menu_file_new.add_command(label=self.trn.msg('htk_gui_menu_file_new_directory'), command=self.explorer.new_directory)
        menu_file_new.add_command(label=self.trn.msg('htk_gui_menu_file_new_project'), command=self.explorer.new_project)
        menu_file_new.add_command(label=self.trn.msg('htk_gui_menu_file_new_helper'), command=self.explorer.new_helper)
        menu_file_new.add_command(label=self.trn.msg('htk_gui_menu_file_new_library'), command=self.explorer.new_library)
        menu_file_new.add_command(label=self.trn.msg('htk_gui_menu_file_new_test'), command=self.explorer.new_test)
        menu_file_new.add_command(label=self.trn.msg('htk_gui_menu_file_new_archive'), command=self.explorer.new_archive)
        menu_file_new.add_command(label=self.trn.msg('htk_gui_menu_file_new_draft'), command=self.explorer.new_draft)

        # menu items
        menu_file.add_command(label=self.trn.msg('htk_gui_menu_file_open'), accelerator='Ctrl+O', command=self.editor.open_file)
        menu_file.add_command(label=self.trn.msg('htk_gui_menu_file_save_as'), command=self.editor.save_as_file, state=tk.DISABLED)
        menu_file.add_command(label=self.trn.msg('htk_gui_menu_file_save'), accelerator='Ctrl+S', command=self.editor.save_file, state=tk.DISABLED)
        menu_file.add_separator()
        menu_file.add_command(label=self.trn.msg('htk_gui_menu_file_exit'), accelerator='Ctrl+Q', command=self._exit)

        # shortcuts
        self.bind('<Control-n>', self.editor.new_file)
        self.bind('<Control-o>', self.editor.open_file)
        self.bind('<Control-s>', self.editor.save_file)
        self.bind('<Control-q>', self._exit)

    def _set_menu_edit(self):
        """Method sets edit menu

        Args:
            none

        Returns:
            void

        """
        
        menu_edit = tk.Menu(self._menu_bar, tearoff=False)
        self._menus['edit'] = menu_edit
        self._menu_bar.add_cascade(label=self.trn.msg('htk_gui_menu_edit'), menu=menu_edit)

        # menu items
        menu_edit.add_command(label=self.trn.msg('htk_gui_menu_edit_undo'), accelerator='Ctrl+Z', command=self.editor.undo, state=tk.DISABLED)
        menu_edit.add_command(label=self.trn.msg('htk_gui_menu_edit_redo'), accelerator='Ctrl+Y', command=self.editor.redo, state=tk.DISABLED)
        menu_edit.add_separator()
        menu_edit.add_command(label=self.trn.msg('htk_gui_menu_edit_cut'), accelerator='Ctrl+X', command=self.editor.cut, state=tk.DISABLED)
        menu_edit.add_command(label=self.trn.msg('htk_gui_menu_edit_copy'), accelerator='Ctrl+C', command=self.editor.copy, state=tk.DISABLED)
        menu_edit.add_command(label=self.trn.msg('htk_gui_menu_edit_paste'), accelerator='Ctrl+V', command=self.editor.paste, state=tk.DISABLED)
        menu_edit.add_command(label=self.trn.msg('htk_gui_menu_edit_delete'), accelerator='Delete', command=self.editor.delete, state=tk.DISABLED)
        menu_edit.add_command(label=self.trn.msg('htk_gui_menu_edit_select_all'), accelerator='Ctrl+A', command=self.editor.select_all, state=tk.DISABLED)
        menu_edit.add_separator()
        menu_edit.add_command(label=self.trn.msg('htk_gui_menu_edit_goto'), accelerator='Ctrl+G', command=self.editor.win_goto, state=tk.DISABLED)
        menu_edit.add_command(label=self.trn.msg('htk_gui_menu_edit_find'), accelerator='Ctrl+F', command=self.editor.win_find, state=tk.DISABLED)
        menu_edit.add_command(label=self.trn.msg('htk_gui_menu_edit_replace'), accelerator='Ctrl+R', command=self.editor.win_replace, state=tk.DISABLED)

        # shorcuts
        self.bind('<Control-a>', self.editor.select_all)
        self.bind('<Control-g>', self.editor.win_goto)
        self.bind('<Control-f>', self.editor.win_find)
        self.bind('<Control-r>', self.editor.win_replace)

    def _set_menu_view(self):
        """Method sets view menu

        Args:
            none

        Returns:
            void

        """

        menu_view = tk.Menu(self._menu_bar, tearoff=False)
        self._menus['view'] = menu_view
        self._menu_bar.add_cascade(label=self.trn.msg('htk_gui_menu_view'), menu=menu_view)

        # menu items
        menu_view.add_checkbutton(label=self.trn.msg('htk_gui_menu_view_show_line_number'), variable=self.editor.var_show_line_number, command=self.editor.show_line_number)
        menu_view.add_checkbutton(label=self.trn.msg('htk_gui_menu_view_show_info_bar'), variable=self.editor.var_show_info_bar, command=self.editor.show_info_bar)
        menu_view.add_separator()
        menu_view.add_command(label=self.trn.msg('htk_gui_menu_view_increase_font'), accelerator='Ctrl+MouseUp', command=self.editor.increase_font, state=tk.DISABLED)
        menu_view.add_command(label=self.trn.msg('htk_gui_menu_view_decrease_font'), accelerator='Ctrl+MouseDown', command=self.editor.decrease_font, state=tk.DISABLED)

    def _set_menu_plugin(self):
        """Method sets plugin menu

        Args:
            none

        Returns:
            void

        """

        self._pluginmanager = PluginManager.get_instance()
        menu_plugin = tk.Menu(self._menu_bar, tearoff=False)
        self._menus['plugin'] = menu_plugin
        self._menu_bar.add_cascade(label=self.trn.msg('htk_gui_menu_plugin'), menu=menu_plugin)

        # menu items
        menu_plugin.add_command(label=self.trn.msg('htk_gui_menu_plugin_manager'), command=self.pluginmanager.show_manager)
        menu_plugin.add_separator()

    def _set_menu_help(self):
        """Method sets help menu

        Args:
            none

        Returns:
            void

        """
 
        self._help = Help.get_instance()
        menu_help = tk.Menu(self._menu_bar, tearoff=False)
        self._menus['help'] = menu_help
        self._menu_bar.add_cascade(label=self.trn.msg('htk_gui_menu_help'), menu=menu_help)
        menu_help.add_command(label=self.trn.msg('htk_gui_menu_help_web_tutor'), command=self.help.web_tutor)
        menu_help.add_command(label=self.trn.msg('htk_gui_menu_help_web_doc'), command=self.help.web_doc)
        menu_help.add_separator()
        menu_help.add_command(label=self.trn.msg('htk_gui_menu_help_about'), command=self.help.win_about)

    def _set_toolbar(self):
        """Method sets toolbar

        Args:
            none

        Returns:
            void

        """
        
        self.set_tool('new', 'new.gif', 'htk_gui_menu_file_new', self.editor.new_file)
        self.set_tool('open', 'open.gif', 'htk_gui_menu_file_open', self.editor.open_file)
        self.set_tool('save', 'save.gif', 'htk_gui_menu_file_save', self.editor.save_file, False)
        self.set_tool('undo', 'undo.gif', 'htk_gui_menu_edit_undo', self.editor.undo, False)
        self.set_tool('redo', 'redo.gif', 'htk_gui_menu_edit_redo', self.editor.redo, False)
        self.set_tool('cut', 'cut.gif', 'htk_gui_menu_edit_cut', self.editor.cut, False)
        self.set_tool('copy', 'copy.gif', 'htk_gui_menu_edit_copy', self.editor.copy, False)
        self.set_tool('paste', 'paste.gif', 'htk_gui_menu_edit_paste', self.editor.paste, False)
        self.set_tool('delete', 'delete.gif', 'htk_gui_menu_edit_delete', self.editor.delete, False)
        self.set_tool('find', 'find.gif', 'htk_gui_menu_edit_find', self.editor.win_find, False)

    def set_tool(self, key, image, tooltip, command, enable=True):
        """Method sets tool button

        Args:
            key (str): tool key
            image (str): image file
            tooltip (str): langtext
            command (callback): command
            enable (bool): enable tool

        Returns:
            void

        """

        if (key not in self._images):
            self._images[key] = tk.PhotoImage(file=path.join(self._imgdir, image))
        state = tk.NORMAL if (enable) else tk.DISABLED
        btn = tk.Button(self._tool_bar, command=command, image=self._images[key], relief=tk.FLAT, state=state)
        btn.image = self._images[key]
        btn.pack(side=tk.LEFT)
        self._tools[key] = btn
        
        self._tooltips[key] = ToolTip(btn, self.trn.msg(tooltip))

    def _set_pane_left(self):
        """Method sets left pane

        Args:
            none

        Returns:
            void

        """

        self._pane_left = tk.PanedWindow(self._pane_main, orient=tk.VERTICAL, sashwidth=10, sashrelief=tk.RAISED)
        self._pane_main.add(self._pane_left)
        self._set_explorer()
        self._set_yoda_tree()

    def _set_pane_right(self):
        """Method sets right pane

        Args:
            none

        Returns:
            void

        """

        self._pane_right = tk.PanedWindow(self._pane_main, orient=tk.VERTICAL, sashwidth=10, sashrelief=tk.RAISED)
        self._pane_main.add(self._pane_right)
        self._set_editor()
        self._set_logger()

    def _set_explorer(self):
        """Method sets explorer frame

        Args:
            none

        Returns:
            void

        """

        self._explorer = Explorer.get_instance(self)
        self._pane_left.add(self.explorer)

    def _set_yoda_tree(self):
        """Method sets yoda tree frame

        Args:
            none

        Returns:
            void

        """

        self._yoda_tree = YodaTree.get_instance(self)
        self._pane_left.add(self.yoda_tree)

    def _set_editor(self):
        """Method sets editor frame

        Args:
            none

        Returns:
            void

        """

        self._editor = Editor.get_instance(self)
        self._pane_right.add(self.editor)

    def _set_logger(self):
        """Method sets logger frame

        Args:
            none

        Returns:
            void

        """

        self._logger = Logger.get_instance(self)
        self._pane_right.add(self.logger)

    def _load_plugins(self):
        """Method loads plugins

        Args:
            none

        Returns:
            void

        """

        for name, cfg in self.cfg.data['Plugins'].items():
            if (name not in self._plugins):
                if ('enabled' in cfg and cfg['enabled'] == 1):
                    full_path = cfg['package'] + '.' + cfg['module']
                    mod = __import__(full_path)
                    components = full_path.split('.')

                    for comp in components[1:]:
                        mod = getattr(mod, comp)
                    plugin = mod.Plugin(self)
                    self._plugins[plugin.plugin_id] = plugin

    def _exit(self, event=None):
        """Method stops application

        Args:
            event (obj): event

        Returns:
            void

        """

        res = tkmsg.askyesno(self.trn.msg('htk_gui_exit_title'), self.trn.msg('htk_gui_exit_question'))
        if (res):
            self.editor.save_tabs()
            self.logger.info(self.trn.msg('htk_core_stopped'))
            self.logger.logfile.close()
            self.destroy()

class ExceptionHandler:
    """Class ExceptionHandler
    """

    _logger = None

    def __init__(self, func, subst, widget):
        """Class constructor

        Called when object is initialized

        Args:
           func (obj): function
           subst (obj): substrate
           widget (obj): widget

        """

        self.func = func
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        """Method catches unhandled exception

        Args:
            args (list): arguments

        Returns:
            obj

        """

        try:
            if self.subst:
                args = self.subst(*args)
            return self.func(*args)

        except Exception as e:
            if (self._logger is None):
                self._logger = Logger.get_instance()
            self._logger.error(traceback.format_exc())
