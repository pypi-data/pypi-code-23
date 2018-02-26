# -*- coding: utf-8 -*-
"""ToolTip widget

.. module:: client.core.ooltip
   :platform: Windows, Unix
   :synopsis: ToolTip widget
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

from hydratk.extensions.client.core.tkimport import tk

class ToolTip(object):
    """Class ToolTip
    """    
    
    _parent = None
    _text = None
    _win = None

    def __init__(self, parent, text):
        """Class constructor

        Called when object is initialized

        Args:
           parent (obj): parent widget
           text (str): tooltip text

        Raises:
           error: ValueError

        """
        
        self._parent = parent
        self._text = text

        self._parent.bind('<Enter>', self._display)
        self._parent.bind('<Leave>', lambda f: self._win.destroy())
        
    def _display(self, event=None):
        """Method displays tooltip

        Args:
            event (obj): event

        Returns:
            void

        """
        
        x, y, cx, cy = self._parent.bbox('insert')
        x += self._parent.winfo_rootx() + 25
        y += self._parent.winfo_rooty() + 20

        self._win = tk.Toplevel(self._parent)
        self._win.wm_overrideredirect(True)
        self._win.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self._win, text=self._text, justify='left', background='#FFFF00', relief='solid', borderwidth=1)
        label.pack(ipadx=1)
