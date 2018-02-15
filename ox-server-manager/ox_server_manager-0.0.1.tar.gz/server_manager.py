#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
ServerManager

last edit:
15.02.2018

"""


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


import os
import sys
import time
import logging
import re
import socket
from urllib.parse import urlparse
from pprint import pprint

logger = logging.getLogger("ServerManager")





class AddServerWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="AddServerWindow", border_width=25)
        self.connect("destroy", lambda x: Gtk.main_quit())
        self.mainbox = Gtk.VBox()
        self.add(self.mainbox)
        
        self.properties_box = Gtk.VBox()
        self.mainbox.pack_start(self.properties_box, True, True, 0)
        
        for url in ["server_ip", "server_nickurl", "hoster", "domains", "userurls"]:
            box = Gtk.HBox()
            box.set_url(url)
            label = Gtk.Label(url)
            #entry = Gtk.Entry()
            entry = Gtk.TextView()
            entry.set_wrap_mode(Gtk.WrapMode.WORD)
            buffer = entry.get_buffer()
            buffer.set_text(url)
            
            label.set_properties("angle", 12,5)
            label.set_properties("lines", 2)
            label.set_properties("selectable", 0)
            
            box.pack_start(label, True, True, 3)
            box.pack_start(entry, True, True, 3)
            self.properties_box.pack_start(box, True, True, 3)
            
        add_button = Gtk.Button(stock=Gtk.STOCK_ADD)
        add_button.connect("clicked", self.on_add_button_clicked)
        self.mainbox.pack_start(add_button, True, True, 3)
        
        
        self.show_all()

        
    def on_add_button_clicked(self):
        pass

        
    def create_box(self):
        for box in self.properties_box.get_children():
            print (box.get_url())
        #return self.mainbox
        

class Server:
    def __init__(self, name=None, type=None, ip=None, url=None):
        self.name = None
        self.type = None
        self.ip = None
        self.url = None
        if type:
            self.set_type(type)
        if name:
            self.set_name(name)
        if ip:
            self.set_ip(ip)
            
        if url:
            self.set_url(url)


        
    def get_name(self):
        return self.name
        
    def set_name(self, name):
        if isinstance(name, str):
            self.name = name
            
        
        
    def get_type(self):
        return self.type
        
    def set_type(self, type):
        if isinstance(type, str):
            self.type = type
        
            
            
    def get_ip(self):
        return self.ip
        
    def set_ip(self, ip):
        try:
            test = socket.inet_pton(socket.AF_INET, ip)
            self.ip = ip
        except Exception as e:
            logger.error("could not set ip address: %s", e)



    def get_url(self):
        return self.url
        
    def set_url(self, url):
        if self.verify_url(url):
            self.url = url
        else:
            logger.error("could not set url: %s", url)



    def verify_url(self, url):
        url = url.strip()
        if url[-1] == ".":
            url = url[:-1]
        if url[-1] == "/":
            url = url[:-1]
        url = url.replace("https://", "") 
        url = url.replace("http://", "") 
        if url.startswith("www."):
            url = url.replace("www.", "")
        URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:[a-z0-9]{2,5}|.)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:[a-z0-9]{2,5})\b/?(?!@)))"""
        if re.match(URL_REGEX, url):
            return url




class ServerManager():
        
    def __init__(self):
        self.preferences_path = os.path.join(os.path.expanduser('~'), '.config/server_manager/')
        self.get_preferences()

    def get_preferences(self):
        logger.debug("get_preferences")
        if not os.path.exists(self.preferences_path):
            os.makedirs(self.preferences_path)
        
    def add_server(self,
        name=None,
        type=None,
        ip=None,
        url=None):
        logger.debug("add_server")
        
        server = Server()
        
        server.set_name(name)
        server.set_ip(ip)
        server.set_url(url)

        
        while server.get_name() == None:
            name = input("please enter server name:\n")
            server.set_name(name)
            
        
        while server.get_type() == None:
            type = input("please enter hosting type:\n")
            server.set_type(type)
            
        while server.get_ip() == None:
            ip = input("please enter server ip:\n")
            server.set_ip(ip)
            
        while server.get_url() == None:
            url = input("please enter server url:\n")
            server.set_url(url)
        return server
            

def main():
    sm = ServerManager()
    Gtk.main()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s (%(lineno)s) - %(levelname)s: %(message)s",
        datefmt='%Y.%m.%d %H:%M:%S',
        )
    logger.setLevel("DEBUG")

    sm = ServerManager()
    s = sm.add_server(
        name = "name test",
        type = "name test",
        ip="1.2.3.4",
        url="example.de")
        
    print(s.name)
    print(s.type)
    print(s.ip)
    print(s.url)
