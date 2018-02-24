#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
ebay api settings editor

last edit:
23.02.2018
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GObject

import os
import sys
import time
import logging
import six
import ruamel.yaml as yaml

from datetime import datetime, timedelta
from pprint import pprint
from threading import Thread
from ebaysdk.trading import Connection as Trading
from optparse import OptionParser

if six.PY2:
    from ConfigParser import SafeConfigParser
else:
    import configparser  as SafeConfigParser

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
    

logger = logging.getLogger("eBayApiSettingsEditor")
logging.getLogger('ebaysdk').setLevel(logging.INFO)
logging.getLogger('urllib3.util.retry').setLevel(logging.INFO)


class eBayApiSettingsEditor(Gtk.Window):
    
    def __init__(self, show_help=False):
        if show_help:
            print('you need help?')
        # config
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        home = os.path.expanduser("~")
        self.config_dir = os.path.join(home, ".ebay")
        self.config_file_path      = os.path.join(self.config_dir, "config.yaml")
        self.config_file_path_test = os.path.join(self.config_dir, "config.yaml")
        self.icons_dir = os.path.join(self.dir_path,  "icons")
        self.config_file_template = os.path.join(self.dir_path, "templates", "api_config.yaml")
        
        logger.debug("looking for config file: %s", self.config_file_path)
        if not os.path.exists(self.config_file_path):
            logger.info("creating config file")
            self.create_config_file_from_template()
        self.config = self.read_config_file()
        if not self.config or self.config == None:
            logger.info("config file is empty")
            self.create_config_file_from_template()
            self.config = self.read_config_file()
            
        # style
        screen = Gdk.Screen.get_default()
        gtk_provider = Gtk.CssProvider()
        gtk_context = Gtk.StyleContext()
        gtk_context.add_provider_for_screen(screen, gtk_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        css = b"""
            *.red_border { border-color : red}
            *.bigger { font: 16}
            *.bold { font: bold}
            """
        gtk_provider.load_from_data(css)

        # window
        Gtk.Window.__init__(self, title="eBay API Tool", border_width=10)
        self.connect("delete-event", Gtk.main_quit)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(700, 700)
        
        iconpath = os.path.join(self.icons_dir, "window_icon.png")
        self.set_icon_from_file(iconpath)
        
        # headerbar
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        headerbar.props.title = "eBay API Tool"
        self.set_titlebar(headerbar)
        
        upper_box = Gtk.VBox()
        self.add(upper_box)
        
        sw = Gtk.ScrolledWindow()
        upper_box.pack_start(sw, True, True, 0)

        self.mainbox = Gtk.VBox(spacing=5)
        self.mainbox.set_border_width(5)
        sw.add(self.mainbox)

        ## connection check box
        self.check_token_box = Gtk.Box()
        box = Gtk.VBox()
        check_token_button = Gtk.Button("Check Token (Sandbox)")
        check_token_button.connect("clicked", self.on_check_token_button_clicked, "sandbox")
        box.pack_start(check_token_button, True, True, 0)
        check_token_button = Gtk.Button("Check Token (Productive)")
        check_token_button.connect("clicked", self.on_check_token_button_clicked,  "productive")
        box.pack_start(check_token_button, True, True, 0)
        self.check_token_box.pack_start(box, True, True, 0)
        self.connection_state_widget = Gtk.Image()
        self.check_token_box.pack_start(self.connection_state_widget, True, True, 0)
        
        ## Location button
        self.location_box = Gtk.Box()
        location_label = Gtk.Label("Location")
        self.location_box.pack_start(location_label, True, True, 0)
        self.location_entry = Gtk.Entry()
        self.location_entry.set_name("location_entry")
        self.location_entry.set_sensitive(0)
        self.location_entry.set_text(self.config_file_path)
        self.location_box.pack_start(self.location_entry, True, True, 0)
        
        # save and quit button
        box = Gtk.HBox()
        self.save_button = Gtk.Button(stock=Gtk.STOCK_SAVE)
        self.save_button.get_image().show()
        self.save_button.connect("clicked", self.on_save_button_clicked)
        box.pack_end(self.save_button, True, True, 0)
        window_quit_button = Gtk.Button(stock=Gtk.STOCK_QUIT)
        window_quit_button.get_image().show()
        window_quit_button.connect("clicked", self.destroy)
        box.pack_start(window_quit_button, True, True, 0)
        
        ## create settings entries box
        self.entries_box = self.create_settings_widget_from_config_file()
        self.mainbox.pack_start(self.entries_box, True, True, 0)
        self.mainbox.pack_start(self.check_token_box, False, False, 0)
        self.mainbox.pack_start(self.location_box, False, False, 0)
        upper_box.pack_start(box, False, False, 0)
        
        self.show_all()
        
    def create_config_file_from_template(self):
        logger.debug("create_config_file_from_template")
        if not os.path.exists(self.config_dir):
            logger.info("creating configfile folder: %s", self.config_dir)
            os.makedirs(self.config_dir)
        logger.debug("reading template: %s", self.config_file_template)
        with open(self.config_file_template, "r") as template_file:
            logger.debug("writing config file: %s", self.config_file_path)
            with open(self.config_file_path, "w") as config_file:
                lines = template_file.readlines()
                config_file.writelines(lines)
            
    def read_config_file(self):
        logger.debug("read_config_file")
        with open(self.config_file_path, "r") as config_file:
            config = yaml.load(config_file, yaml.RoundTripLoader)
            logger.debug("config from yaml.RoundTripLoader:\n%s\n%s", type(config), config)
            if not config:
                self.create_config_file_from_template()
                config = self.read_config_file()
            logger.debug("show config file content: %s", config)
            return config
                    
    def write_config_file(self, test=False):
        logger.debug("write_config_file")
        if test:
            file_path = os.path.join(self.config_dir, "config_test.yaml")
            self.config_file_path_test = file_path
        else:
            file_path = self.config_file_path
        with open(file_path, "w") as config_file:
            logger.info("save to yaml config file from settings")
            self.get_settings_from_widgets()
            save_data = yaml.dump(
                    self.config,
                    Dumper=yaml.RoundTripDumper,
                    default_flow_style=False
                    )
            config_file.writelines(save_data)

    
    def create_settings_widget_from_config_file(self):
        logger.debug("create_settings_widget_from_config_file")
        
        box = Gtk.VBox()
        box.name = "settings_box"
        logger.debug("load values from settings_dict")
        if self.config == None:
            logger.error("self.conf = None")
            return
        for key, value in self.config.items():
            logger.debug("create label for key: %s", key)
            label = Gtk.Label(str(key))
            style_context = label.get_style_context()
            style_context.add_class("bold")
            box.pack_start(label, False, False, 0)
            if isinstance(value, str):
                label = Gtk.Label(value)
                box.pack_start(label, False, False, 0)
                continue
            elif isinstance(value, yaml.comments.CommentedMap):
                for name in value.keys():
                    hbox  = Gtk.HBox()
                    label = Gtk.Label(name)
                    entry = Gtk.Entry()
                    entry.name = name
                    if name in value.keys():
                        if value[name]:
                            entry.set_text(str(value[name]))
                    entry.connect("changed", self.on_property_entry_changed)
                    hbox.pack_start(label, False, False, 10)
                    hbox.pack_start(entry, True, True, 10)
                    box.pack_start(hbox, False, False, 0)
        return box
        
    
    def on_property_entry_changed(self, widget):
        style_context = self.save_button.get_style_context()
        style_context.add_class("red_border")
        self.write_config_file(test=True)



    def get_settings_from_widgets(self, widget=None):
        logger.debug("on_save_button_clicked")
        
        sections = self.config.keys()
        logger.debug("sections = %s", sections)
        widgets = self.entries_box.get_children()
        for widget in widgets:
            logger.debug("widet type = %s", type(widget))
            logger.debug("widet name = %s", widget.get_name())
            
            if widget.get_name() == "GtkLabel":
                section = widget.get_text().strip()
                if section in sections:
                    logger.debug("section = %s", section)
            elif widget.get_name() == "GtkHBox":
                logger.debug("get children from hbox")
                children = widget.get_children()
                for child in children:
                    if child.get_name() == "GtkLabel":
                        sub_section = child.get_text().strip()
                        logger.debug("section = %s", sub_section)
                    elif child.get_name() == "GtkEntry":
                        self.config[section][sub_section] = child.get_text()
        logger.debug("values = %s", self.config)
         
         
    def on_save_button_clicked(self, widget):
        logger.debug("on_save_button_clicked")
        self.write_config_file()
        style_context = widget.get_style_context()
        style_context.remove_class("red_border")

        
    def replace_widget(self, old_widget, new_widget):
        parent = old_widget.get_parent()
        parent.remove(old_widget)
        parent.pack_start(new_widget, True, True, 0)
        new_widget.show()
        return new_widget
                    
                        
    def on_check_token_button_clicked(self, widget, env):
        logger.debug("on_check_token_button_clicked")
        spinner = Gtk.Spinner()
        self.connection_state_widget = self.replace_widget(self.connection_state_widget, spinner)
        spinner.start()
        thread = Thread(target=self.check_token, kwargs={"env" : env})
        thread.start()
        
        
    def check_token(self, widget=None, env=None):
        logger.debug("check_token")
        try:
            if env == "productive":
                api = Trading(config_file=self.config_file_path_test)
                response = api.execute('GetCategories', {})
            elif env == "sandbox":
                api = Trading(config_file=self.config_file_path_test, domain='api.sandbox.ebay.com')
                response = api.execute('GetCategories', {})
            else:
                raise NameError
            self.set_connection_state_icon(True)
        except Exception as e:
            logger.error("could not connect")
            logger.error(e)
            self.set_connection_state_icon(False)
            

    def set_connection_state_icon(self, state):
        logger.debug("""set_connection_state_icon""")
        self.connection_state_widget = self.replace_widget(self.connection_state_widget, Gtk.Image())
        if state:
            self.connection_state_widget.set_from_pixbuf(GdkPixbuf.Pixbuf().new_from_file(os.path.join(self.icons_dir, "face-smile.png")))
        else:
            self.connection_state_widget.set_from_pixbuf(GdkPixbuf.Pixbuf().new_from_file(os.path.join(self.icons_dir, "face-sad.png")))
          
        
    def on_destroy(self, widget=None, data=None):
        messagedialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.WARNING,
            Gtk.ButtonsType.OK_CANCEL, "Really quit?")
        
        response = messagedialog.run()
        messagedialog.destroy()
        if response == Gtk.ResponseType.CANCEL:
            return True
        Gtk.main_quit()

    def destroy(self, widget, data=None):
        Gtk.main_quit()
        
def main():
    parser = OptionParser()
    parser.add_option("-d", "--dd", dest="show_help",
                        help="show help text")
    (options, args) = parser.parse_args()
    rss2sms = eBayApiSettingsEditor(**vars(options))
    print(rss2sms)
    print(type(rss2sms))
    Gtk.main()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s (%(lineno)s) - %(levelname)s: %(message)s", datefmt='%Y.%m.%d %H:%M:%S')
    main()
