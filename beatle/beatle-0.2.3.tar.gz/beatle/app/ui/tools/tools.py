# -*- coding: utf-8 -*-
import wx


from beatle import tran
from beatle.lib import wxx
from beatle.model import Workspace, Folder
from beatle.app.ui.dlg import WorkspaceDialog, FolderDialog

DIALOG_DICT = {
        Workspace: (WorkspaceDialog, 'edit workspace {0}'),
        Folder: (FolderDialog, 'edit folder {0}'),
    }


def edit(parent, obj):
    """Edit the object"""
    t = type(obj)
    if t in DIALOG_DICT:
        v = DIALOG_DICT[t]

        @tran.TransactionalMethod(v[1])
        @wxx.EditionDialog(v[0])
        def editDialog(parent, obj):
            """Handle type edition"""
            return (parent, obj)

        editDialog(parent, obj)
        return True
    return False


def append_menuitem_copy(menu, menuitem):
    """Add a menuitem clone"""
    clone = wx.MenuItem(menu, menuitem.GetId(), menuitem.GetText(), menuitem.GetHelp(), menuitem.GetKind())
    if menuitem.GetBitmap().IsOk():
        clone.SetBitmap(menuitem.GetBitmap())
    menu.AppendItem(clone)
    if menuitem.GetKind() is wx.ITEM_CHECK:
        clone.Check(menuitem.IsChecked())


def set_menu_handlers(frame, imnu, command, update):
    """This method travels through the whole menu
    and submenu structure and set dispatch handlers.
    This method is used for dispatching events to focused
    windows that install the menus"""
    if type(imnu) is wx.Menu:
        for x in imnu.GetMenuItems():
            set_menu_handlers(frame, x, command, update)
    if type(imnu) is wx.MenuItem:
        frame.Bind(wx.EVT_MENU, command, id=imnu.GetId())
        frame.Bind(wx.EVT_UPDATE_UI, update, id=imnu.GetId())


def unset_menu_handlers(frame, imnu, command, update):
    """This method travels through the whole menu
    and submenu structure and unset dispatch handlers.
    This method is used for dispatching events to focused
    windows that install the menus"""
    if type(imnu) is wx.Menu:
        for x in imnu.GetMenuItems():
            set_menu_handlers(frame, x, command, update)
    if type(imnu) is wx.MenuItem:
        frame.Unbind(wx.EVT_MENU, command, id=imnu.GetId())
        frame.Unbind(wx.EVT_UPDATE_UI, update, id=imnu.GetId())


def clone_mnu(imnu, parent=None, enabled=False, notitle=False, separator=False):
    """
    Clone a menu or menuitem recursively. If
    enabled is specified, disabled items are filtered.
    separator makes sense only when parent is not None.
    This case, an separator will be added before the first
    menuitem to be copied.
    """
    if isinstance(imnu, wx.Menu):
        # if we filter disabled elements, we need to update menu first
        if enabled:
            imnu.UpdateUI()
        # if parent is specified the menu items are copied
        # if not, new menu is created
        if parent:
            clone = parent
            if separator:
                pos = clone.GetMenuItemCount()
        else:
            title = (not notitle and imnu.GetTitle()) or wx.EmptyString
            style = imnu.GetStyle()
            separator = False
            clone = wx.Menu(title=title, style=style)
        subs = [clone_mnu(x, clone, enabled) for x in
            imnu.GetMenuItems() if not enabled or x.IsEnabled()]
        subs = [x for x in subs if x is not None]
        if len(subs) > 0:
            # remove begin/adjoint/end separators
            while len(subs) and subs[0].GetKind() == wx.ITEM_SEPARATOR:
                clone.DestroyItem(subs[0])
                del subs[0]
            while len(subs) and subs[-1].GetKind() == wx.ITEM_SEPARATOR:
                clone.DestroyItem(subs[-1])
                del subs[-1]
            for i in range(len(subs) - 1, -1, -1):
                # remove duplicated separators
                if subs[i].GetKind() != wx.ITEM_SEPARATOR:
                    continue
                if subs[i - 1].GetKind() != wx.ITEM_SEPARATOR:
                    continue
                clone.DestroyItem(subs[i])
                del subs[i]
            if len(subs) > 0:
                if separator:
                    clone.InsertSeparator(pos)
                return clone
        if not parent:
            del clone
        return None
    if type(imnu) is wx.MenuItem:
        if enabled and not imnu.IsEnabled():
            return None
        simnu = imnu.GetSubMenu()
        if simnu is not None:
            simnu = clone_mnu(simnu, None, enabled)
        clone = wx.MenuItem(parent, imnu.GetId(), imnu.GetText(), imnu.GetHelp(), imnu.GetKind(), simnu)
        if imnu.GetBitmap().IsOk():
            clone.SetBitmap(imnu.GetBitmap())
        if parent is not None:
            parent.AppendItem(clone)
        if imnu.GetKind() is wx.ITEM_CHECK:
            clone.Check(imnu.IsChecked())
        return clone
