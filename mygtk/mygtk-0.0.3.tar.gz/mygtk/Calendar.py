#!/usr/bin/env python
#-*- coding: utf-8 -*-


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk


import os
import sys
import time
import logging
from datetime import date


logger = logging.getLogger("Calendar")


class Calendar(Gtk.Calendar):
    def __init__(self):
        Gtk.Calendar.__init__(self)
        
    def get_datetime(self):
        logger.debug("get_datetime")
        year, month, day = self.get_date()
        month += 1
        mydate = date(year, month, day)
        print(mydate)
        return date(year, month, day)

        
