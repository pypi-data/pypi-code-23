# -*- coding: utf-8 -*-
"""Plugin base class

.. module:: client.core.plugin
   :platform: Windows, Unix
   :synopsis: Plugin base class
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

import os
from importlib import import_module

from hydratk.extensions.client.core.tkimport import tk

class Plugin(object):
    """Class Plugin
    """

    _plugin_id = 'Undefined'
    _plugin_name = 'Undefined'
    _plugin_version = 'Undefined'
    _plugin_author = 'Undefined'
    _plugin_year = 'Undefined'

    # references
    _root = None
    _config = None
    _trn = None
    _explorer = None
    _yoda_tree = None
    _editor = None
    _logger = None

    _cfg = None

    def __init__(self, root):
        """Class constructor

        Called when object is initialized

        Args:
           root (obj): root frame

        """

        self._root = root
        self._config = self.root.cfg
        self._trn = self.root.trn
        self._explorer = self.root.explorer
        self._yoda_tree = self.root.yoda_tree
        self._editor = self.root.editor
        self._logger = self.root.logger

        self._init_plugin()
        self._cfg = self.config.data['Plugins'][self.plugin_name]
        self._import_messages()
        self._import_images()

        if hasattr(self.__class__, '_setup') and callable(getattr(self.__class__, '_setup')):
            self._setup()

    @property
    def plugin_id(self):
        """ plugin_id property getter """

        return self._plugin_id

    @property
    def plugin_name(self):
        """ plugin_name property getter """

        return self._plugin_name

    @property
    def plugin_version(self):
        """ plugin_version property getter """

        return self._plugin_version

    @property
    def plugin_author(self):
        """ plugin_author property getter """

        return self._plugin_author

    @property
    def plugin_year(self):
        """ plugin_year property getter """

        return self._plugin_year

    @property
    def cfg(self):
        """ cfg property getter """

        return self._cfg

    @property
    def root(self):
        """ root property getter """

        return self._root

    @property
    def config(self):
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

    def _import_messages(self):
        """Methods imports langtexts

        Args:
           none

        Returns:
           void

        """

        msgdir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins/{0}/translation'.format(self.plugin_id))
        if (os.path.exists(msgdir)):
            try:
                msg_package = self.cfg['package'] + '.translation.' + self.trn._language + '.messages'
                lang = import_module(msg_package)
                self.trn._register_messages(lang.msg)
            except ImportError:
                pass

    def _import_images(self):
        """Methods imports images

        Args:
           none

        Returns:
           void

        """

        imgdir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins/{0}/img'.format(self.plugin_id))
        if (os.path.exists(imgdir)):
            for f in os.listdir(imgdir):
                fname, suffix = f.split('.')
                if (suffix == 'gif'):
                    self.root.images[fname] = tk.PhotoImage(file=os.path.join(imgdir, f))

    def _set_tool(self, key, image, tooltip, command, enable=True):
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

        self.root.set_tool(key, image, tooltip, command, enable)
        
    def _set_menu(self, title, label, parent=''):
        """Method sets menu

        Args:
            title (str): menu title, used to register in root.menus
            label (str): langtext
            parent (str): parent menu (must be registered, otherwise will be added to menubar)

        Returns:
            void

        """
        
        if (parent in self.root.menus):
            menu = tk.Menu(self.root.menus[parent], tearoff=False)
            self.root.menus[title] = menu
            self.root.menus[parent].add_cascade(label=self.trn.msg(label), menu=menu)
        else:
            menu = tk.Menu(self.root.menu_bar, tearoff=False)
            self.root.menus[title] = menu
            idx = self.root.menu_bar.index(tk.END)
            self.root.menu_bar.insert_cascade(idx, label=self.trn.msg(label), menu=menu)

    def _set_menu_item(self, menu, label, command, shortcut=None, event=None, enable=True):
        """Method sets menu item

        Args:
            menu (str): menu title (must be registered in root.menus)
            label (str): langtext
            command (cb): callback
            shortcut (str): shortcut string
            event (str): event to bind shortcut
            enable (bool): status

        Returns:
            void

        """
        
        if (menu in self.root.menus):
            menu = self.root.menus[menu]
            state = tk.NORMAL if (enable) else tk.DISABLED
            menu.add_command(label=self.trn.msg(label), accelerator=shortcut, command=command, state=state)
            if (event is not None):
                self.root.bind(event, command)
