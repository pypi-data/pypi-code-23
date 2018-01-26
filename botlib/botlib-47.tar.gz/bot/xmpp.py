# BOTLIB - Framework to program bots !!
# -*- coding: utf-8 -*-
#
# bot/xmpp.py
#
# Copyright 2017,2018 B.H.J Thate
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice don't have to be included.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# 9-1-2018 As the creator of this file, I disclaim all rights on  this file. 
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" xmpp bot (requires sleekxmpp). """

from bot import Bot
from bot.event import Event
from bot.handler import Handler
from bot.obj import Config, Default, Object
from bot.thr import Launcher
from bot.users import Users
from bot.utils.misc import stripped
from bot.utils.trace import get_exception

import os
import logging
import ssl
import time

class XMPP(Bot, Handler):

    """" XMPP bot based on sleekxmpp. """

    cc = ""

    def __init__(self, *args, **kwargs):
        Bot.__init__(self, *args, **kwargs)
        Handler.__init__(self, *args, **kwargs)
        self._connected = Object()
        self._threaded = False
        self.channels = []
        
    def _connect(self, user, pw):
        """ connect to the xmpp server. """
        self._makeclient(user, pw)
        logging.warn("connect %s" % user)
        if self.noresolver:
            self.client.configure_dns(None)
        if self.openfire:
            self.client.connect(use_ssl=True)
        else:
            self.client.connect(reattempt=False, use_tls=True, use_ssl=False)
                        
    def _makeclient(self, jid, password):
        """ create a sleekxmpp client to use. """
        try:
            import sleekxmpp.clientxmpp
            import sleekxmpp
        except ImportError:
            logging.warn("sleekxmpp is not installed")
            return
        self.client = sleekxmpp.clientxmpp.ClientXMPP(jid, password, plugin_config={}, plugin_whitelist=[], escape_quotes=False, sasl_mech=None)
        self.client.reconnect_max_attempts = 3
        self.client._counter = Default(_default=0)
        self.client._error = Object()
        self.client._time = Default(_default=0)
        self.client._time.start = time.time()
        self.client.use_ipv6 = self.use_ipv6
        if self.no_certs:
            self.client.server_hostname = True
            self.client.XMPP_CA_CERT_FILE = None
            self.client.ca_certs = ssl.CERT_NONE
            self.client.verify_flags = ssl.VERIFY_CRL_CHECK_LEAF
        if self.openfire:
            self.client.ssl_version = ssl.PROTOCOL_SSLv3
        self.client.register_plugin(u'xep_0030')
        self.client.register_plugin(u'xep_0045')
        self.client.register_plugin(u'xep_0199')
        self.client.register_plugin(u'xep_0203')
        self.client.add_event_handler("session_start", self.session_start)
        self.client.add_event_handler("message", self.messaged)
        self.client.add_event_handler("iq", self.iqed)
        self.client.add_event_handler("ssl_invalid_cert", self.invalid_cert)
        self.client.add_event_handler('disconnected', self.disconnected)
        self.client.add_event_handler('connected', self.connected)
        self.client.add_event_handler('presence_available', self.presenced)
        self.client.add_event_handler('presence_dnd', self.presenced)
        self.client.add_event_handler('presence_xa', self.presenced)
        self.client.add_event_handler('presence_chat', self.presenced)
        self.client.add_event_handler('presence_away', self.presenced)
        self.client.add_event_handler('presence_unavailable', self.presenced)
        self.client.add_event_handler('presence_subscribe', self.presenced)
        self.client.add_event_handler('presence_subscribed', self.presenced)
        self.client.add_event_handler('presence_unsubscribe', self.presenced)
        self.client.add_event_handler('presence_unsubscribed', self.presenced)
        self.client.add_event_handler('groupchat_presence', self.presenced)
        self.client.add_event_handler('groupchat_subject', self.presenced)
        self.client.add_event_handler('failed_auth', self.failedauth)
        self.client.exception = self.exception
        self.client.use_signals()
        
    def announce(self, txt):
        """ announce text on the joined channels. """
        for channel in self.channels:
            self.say(channel, txt)

    def connect(self, user, passwd=""):
        """ connect to the xmpp server. """
        if not passwd:
            fn = os.path.expanduser("~/.sleekpass")
            pww = ""
            f = open(fn, "r")
            pww = f.read()
            f.close()
            passwd = pww.strip()
        self.passwd = passwd
        self.user = user
        self.server = stripped(self.user.split("@")[-1])
        self._connect(user, self.passwd)
        self._connected.ready()
        
    def connected(self, data):
        """ called when the bot is connected to the server. """
        logging.warn("connected to %s" % self.server)
                 
    def disconnected(self, data):
        """ disconnedted callback. """
        logging.warn("disconnected from %s" % self.server)

    def exception(self, data):
        """ exception callback. """
        logging.error("error %s" % data)

    def failedauth(self, data):
        """ failedauth callback. """
        logging.info("failed auth %s" % data)

    def failure(self, data):
        """ failure callback. """
        logging.info("failure %s" % data)

    def invalid_cert(self, data):
        """ invalid certifcate callback. """
        logging.info("invalid cert %s" % data)

    def iqed(self, data):
        """ iq callback. """
        logging.warn("! %s" % data)

    def join(self, nick, room):
        self._connected.wait()
        if not room or "#" in room:
            return
        logging.warn("join %s as %s" % (room, nick))
        if room not in self.channels:
            self.channels.append(room)
        self.client.plugin['xep_0045'].joinMUC(room,
                                    nick,
                                    wait=False)

    def messaged(self, data):
        """ function to handle messages from server. """
        from bot.core import users
        m = Event()
        m.update(data)
        m.id = self.id
        if data["type"] == "error":
            logging.error("error %s" % m.error)
            return
        if data["type"] == "groupchat":
            m.cc = "!"
            users._userhosts[m.nick] = str(m["from"])
            m.channel = m.origin
        else:
            m.cc = ""
        m["from"] = str(m["from"])
        if self.user in m["from"]:
            logging.warn("ignore %s %s" % (m.type, m["from"]))
            return
        m.origin = m["from"]
        m.room = stripped(m.origin)
        m.server = self.server
        m.channel = m.origin
        m.to = m.origin
        m.txt = m["body"]
        m.cb = "Message"
        if '<delay xmlns="urn:xmpp:delay"' in str(data):
            logging.warn("ignore %s" % m.origin)
            return
        self.put(m)

    def pinged(self, event):
        """ ping callback. """
        logging.info(event)

    def presenced(self, data):
        """ function to handle presences. """
        from bot.core import users
        o = Event()
        o.update(data)
        o.id = self.id
        o.server = self.server
        o.cc = ""
        o.origin = str(data["from"])
        if "txt" not in o:
            o.txt = ""
        o.element = "presence"
        if self.user in o.origin:
            logging.warn("ignore %s" % o.origin)
            return
        user = o.origin
        o.nick = o.origin.split("/")[-1]
        if o.type == 'subscribe':
            pres = Event({'to': o["from"], 'type': 'subscribed'})
            self.client.send_presence(dict(pres))
            pres = Event({'to': o["from"], 'type': 'subscribe'})
            self.client.send_presence(dict(pres))
        o.txt = o.type
        o.cb = "Presence"
        users._userhosts[o.nick] = o.origin

    def resume(self):
        """ method called when resuming the bot. """
        pass

    def say(self, jid, txt, type="chat"):
        """ say test to xmpp user. """
        import sleekxmpp
        try:
            sleekxmpp.jid.JID(jid)
        except sleekxmpp.jid.InvalidJID:
            logging.warn("wrong jid %s" % jid)
            return
        if self.user in jid:
            logging.warn("not writing to self.")
            return
        if jid in self.channels:
            type = "groupchat"
        if type == "groupchat":
            jid = stripped(jid)
        logging.warn("> %s %s %s" % (jid, type, txt))
        self.client.send_message(mto=jid,
                                 mbody=txt,
                                 mtype=type)
         
    def session_start(self, data):
        """ send a presence on startup. """
        logging.info("session start %s" % data)
        self.client.send_presence()
        self.client.get_roster()
        
    def sleek(self):
        """ server function of the xmpp bot. """
        self._connected.wait()
        if "client" in self and self.client:
            try:
                self.client.process()
            except Exception as ex:
                logging.error(get_exception())

    def stop(self):
        """ stop the xmpp bot. """
        if "client" in self and self.client:
            self.client.disconnect()
        super().stop()

    def start(self, *args, **kwargs):
        """ start the xmpp bot. """
        lhr = Launcher()
        self._nrreconnect = 2
        Bot.start(self, *args, **kwargs)
        Handler.start(self)
        self.walk("bot")
        lhr.launch(self.sleek)
