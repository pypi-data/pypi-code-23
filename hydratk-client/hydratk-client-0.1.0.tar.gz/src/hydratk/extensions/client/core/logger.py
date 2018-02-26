# -*- coding: utf-8 -*-
"""Logger frame

.. module:: client.core.logger
   :platform: Windows, Unix
   :synopsis: Logger frame
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

from datetime import datetime
from os import path
from sys import prefix

from hydratk.extensions.client.core.utils import fix_path
from hydratk.extensions.client.core.tkimport import tk, tkst

class Logger(tk.LabelFrame):
    """Class Logger
    """
    
    _instance = None
    _instance_created = False

    # references
    _root = None
    _trn = None
    _config = None

    # gui elements
    _log = None
    _menu = None

    # log parameters
    _log_levels = {
                   'ERROR': 1,
                   'WARN': 2,
                   'INFO': 3,
                   'DEBUG': 4
    }
    _level = None
    _msg_format = None
    _logdir = None
    _logfile = None
    
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

        tk.LabelFrame.__init__(self, self.root.pane_right, text=self.trn.msg('htk_gui_log_label'))
        self._set_gui()
        self._parse_config()

    @staticmethod
    def get_instance(root=None):
        """Method gets Logger singleton instance

        Args:
            root (obj): root frame

        Returns:
            obj

        """

        if (Logger._instance is None):
            Logger._instance_created = True
            Logger._instance = Logger(root)

        return Logger._instance

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
    def logfile(self):
        """ logfile property getter """

        return self._logfile

    def _parse_config(self):
        """Method parses configuration

        Args:
            none

        Returns:
            void

        """

        cfg = self.config.data['Core']['logger']
        self._level = self._log_levels[cfg['level']]
        self._msg_format = cfg['format']

        self._logdir = path.join(prefix, 'var/local/hydratk/client/log') if (cfg['logdir'] == 'default') else cfg['logdir']
        self._logfile = open(fix_path(path.join(self._logdir, datetime.now().strftime('%Y%m%d') + '.log')), 'a')

    def _set_gui(self):
        """Method sets graphical interface

        Args:
            none

        Returns:
            void

        """

        self._log = tkst(self, state=tk.DISABLED, background='#FFFFFF')
        self._log.pack(expand=True, fill=tk.BOTH)
        self._log.tag_config('error', foreground='#FF0000')
        self._log.focus_set()
        self._set_menu()

    def _set_menu(self):
        """Method sets menu

        Args:
            none

        Returns:
            void

        """

        self._menu = tk.Menu(self._log, tearoff=False)
        self._menu.add_command(label=self.trn.msg('htk_gui_log_menu_clear'), command=self._clear)

        self._log.bind('<Button-3>', self._context_menu)

    def _context_menu(self, event=None):
        """Method sets context menu

        Args:
            event (obj): event

        Returns:
            void

        """

        self._menu.tk_popup(event.x_root, event.y_root)

    def _write_msg(self, msg, level=3):
        """Method writes to log (GUI and file)

        Args:
            msg (str): message
            level (int): level, 1-ERROR, 2-WARN, 3-INFO, 4-DEBUG

        Returns:
            void

        """

        if (self._level >= level):
            level = list(self._log_levels.keys())[list(self._log_levels.values()).index(level)]
            msg = self._msg_format.format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), level=level, message=msg)
            self._log.configure(state=tk.NORMAL)
            self._log.mark_set(tk.INSERT, tk.END)
            self._log.insert(tk.INSERT, msg + '\n')
            
            if (level in ['ERROR', 'WARN']):
                idx = self._log.index(tk.INSERT)
                self._log.tag_add('error', '{0}-{1}c'.format(idx, len(msg) + 1), idx)

            self._log.mark_set(tk.INSERT, tk.END)
            self._log.see('end')
            self._log.configure(state=tk.DISABLED)

            self._logfile.write(msg + '\n')
            self._logfile.flush()

    def debug(self, msg):
        """Method writes DEBUG message

        Args:
            msg (str): message

        Returns:
            void

        """

        self._write_msg(msg, 4)

    def info(self, msg):
        """Method writes INFO message

        Args:
            msg (str): message

        Returns:
            void

        """

        self._write_msg(msg, 3)

    def warn(self, msg):
        """Method writes WARN message

        Args:
            msg (str): message

        Returns:
            void

        """

        self._write_msg(msg, 2)

    def error(self, msg):
        """Method writes ERROR message

        Args:
            msg (str): message

        Returns:
            void

        """

        self._write_msg(msg, 1)

    def _clear(self, event=None):
        """Method clears log

        Args:
            event (obj): event

        Returns:
            void

        """

        self._log.configure(state=tk.NORMAL)
        self._log.delete('1.0', 'end')
        self._log.configure(state=tk.DISABLED)
