# -*- coding: utf-8 -*- 
'''
This module provides code to send pop-up notifications to
org.freedesktop.Notifications using dbus.
It provides the write() function which is the simplest interface,
and also the Messenger class which allows setting some additional options.
'''
import logging
import dbus
import sys
import os
import time

DEFAULT_APPNAME = 'Messenger'
DEFAULT_TITLE = ''
DEFAULT_POPTIME = 5 # seconds
DEFAULT_ICON = ''
STALE_TIME = DEFAULT_POPTIME * 20
XDG_CACHE_HOME = os.environ.get('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))
CACHE_DIR = os.path.join(XDG_CACHE_HOME, 'python-dbusnotify')

def get_cache_file(fname, mode=0o700, stale_time=STALE_TIME):
    try:
        os.mkdir(CACHE_DIR, mode=mode)
    except FileNotFoundError:
        os.makedirs(CACHE_DIR, mode=mode)
    except FileExistsError:
        pass
    fpath = os.path.join(CACHE_DIR, fname)

    def is_stale():
        try:
            dt = time.time() - os.path.getmtime(fpath)
        except FileNotFoundError:
            return True
        return True if dt >= stale_time else False

    mode = 'w+' if is_stale() else 'a+'
    # print('mymode', mode)
    fil = open(fpath, mode=mode)
    fil.seek(0)
    return fil


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
    _gtk_icons = Gtk.stock_list_ids()
except ImportError:
    logger.warning(
        'Could not import Gtk. dbusnotify.py'
        ' will not be able to render stock gtk icons'
    )
    _gtk_icons = []


class Icon:
    '''
    Users will only use this class as a container of icons under
    Icon.gtk. For example,
    write('Disk is full!', icon=Icon.gtk.harddisk)

    This class as used by Messenger class controls self.hints
    and self.icon attributes based on an input icon string.
    If the icon string is found in self.gtk_icons the 
    self.hints['icon_data'] is set accordingly,
    and self.icon is unset. In all other cases the icon string is
    just stored in self.icon.
    '''
    _gtk_icons = _gtk_icons
    class gtk:
        "Container for the stock gtk icons"
        pass
    for icon in _gtk_icons:
        setattr(gtk, icon.lstrip('gtk-').replace('-', '_'), icon)

    def __init__(self, icon):
        self.icon = icon
        self.dbus_icon = icon
        self.hints = {}
        if self.icon in self._gtk_icons:
            self._get_gtk_icon()

    def _get_gtk_icon(self):
        name = self.icon.split('-')
        name = '_'.join(map(str.upper, ['STOCK',] + name[1:]))
        icon_attrib_name = getattr(Gtk, name)
        icon = Gtk.Button().render_icon(
            icon_attrib_name,
            Gtk.IconSize.DIALOG)
        struct = (
        icon.get_width(),
        icon.get_height(),
        icon.get_rowstride(),
        icon.get_has_alpha(),
        icon.get_bits_per_sample(),
        icon.get_n_channels(),
        dbus.ByteArray(icon.get_pixels())
        )
        self.hints['icon_data'] = struct
        self.dbus_icon = ''

class Messenger(object):
    """
    The specification is given at:
    https://developer.gnome.org/notification-spec/
    """
    _item             = "org.freedesktop.Notifications"
    _path              = "/org/freedesktop/Notifications"
    _actions_list      = ''

    def __init__(self, title=DEFAULT_TITLE, icon=DEFAULT_ICON,
                 poptime=DEFAULT_POPTIME, replace=False, app_name=DEFAULT_APPNAME,
                 **kwargs):
        self.hints = {}
        
        self.title = str(title)
        self.icon = icon
        self.poptime = poptime
        self.replace = replace
        self.app_name = app_name
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._interface = dbus.Interface(self._address, self._item)


    @property
    def id_file(self):
        try:
            return self._id_file
        except AttributeError:
            self._id_file = get_cache_file(self.app_name)
        return self._id_file

    @id_file.deleter
    def id_file(self):
        try:
            idf = self._id_file
        except AttributeError:
            return
        idf.close()
        del self._id_file

    @property
    def bus(self):
        try:
            return self._bus
        except AttributeError:
            self._bus = dbus.SessionBus()
        return self._bus

    @property
    def id(self):
        try:
            return self._id
        except AttributeError:
            try:
                self.id_file.seek(0)
                line = self.id_file.readline()
                # print('line from cached file:', line)
                self.id = int(line)
            except ValueError:
                self.id = 1
        return self._id

    @id.setter
    def id(self, value):
        self._id = int(value)
        idf = self.id_file
        idf.seek(0)
        idf.truncate()
        idf.write('{:d}\n'.format(self._id))
        idf.seek(0)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    @property
    def icon(self):
        try:
            return self._icon
        except AttributeError:
            return ''

    @icon.setter
    def icon(self, val):
        ic = Icon(val)
        self._icon = ic.dbus_icon
        self.hints.update(ic.hints)

    @property
    def _address(self):
        return self.bus.get_object(self._item, self._path)

    def write(self, message):
        '''
        write() sends a message to the DBUS notification system.
        message needs to be a string or unicode object.
        '''
        message = str(message)
        title = self.title
        def logvar(x, variables=locals()):
            var = variables[x]
            logger.debug(('Messenger.write()', x, type(var), var))
        logvar('message')
        logvar('title')
        # self._get_interface()
        this_id = self._interface.Notify(
            self.app_name,
            self.id if self.replace else 0,
            self.icon,
            title,
            message,
            self._actions_list,
            self.hints,
            self._poptime_in_ms(),
        )
        self.id = this_id
        return this_id

    def _poptime_in_ms(self):
        return 1000 * self.poptime

    def close_notification(self, nid=None):
        if nid:
            self._interface.CloseNotification(nid)
            return
        self._interface.CloseNotification(self.id)

    def close(self):
        self.bus.close()
        del self.id_file

def write(message, title=DEFAULT_TITLE,
          poptime=DEFAULT_POPTIME, icon=DEFAULT_ICON,
          replace_last=False, app_name=DEFAULT_APPNAME):
    '''
    This writes a message to org.freedesktop.Notifications
    using dbus. In other words the message will pop-up on the desktop.
    
    message       : the message to be displayed, object will be converted to str
    title         : title in bold above message
    poptime       : time in seconds for the notification to be displayed
    icon          : Path to a png file to be displayed. If Gtk is available
                    the gtk stock icons can also be used; these can be found
                    under Icon.gtk.
    replace_last  : replace previous notification from app_name
    app_name      : name describing application calling write(...)

    Usage :
        write('Test eight floppy', icon=Icon.gtk.floppy) # using Gtk
        write([1,2,3], icon='/path/to/image.png', poptime=20)
    '''
    with Messenger(
            title=title,
            icon=icon,
            poptime=poptime,
            replace=replace_last,
            app_name=app_name,
    ) as m:
        return m.write(message)
        
__all__ = ['Icon', 'Messenger', 'write']

