"""
    wxx.Menu
    This class improves the creation of menus.
"""

import wx

class Menu(wx.Menu):
    """Quick menu"""
    def __init__(self, *args):
        """Create a new menu.
         args: submenu_descr: list of arrays. Each entry must have the form:
             [identifier, itemtext, helpstring, kind, bitmap]
            for insert a menu item 
        or 
            []
            for insert a separator
        The identifier is the message identifier triggered by the menu.
        The bitmap may be not specified. 
        """
        super(Menu, self).__init__()
        for element in args:
            assert type(element) is list
            if len(element) is 0:
                self.AppendSeparator()
                continue
            assert len(element) in [4,5]
            menu_item = wx.MenuItem(self, *tuple(element[:4]))
            if len(element) == 5:
                menu_item.SetBitmap(element[4])
            self.AppendItem(menu_item)
