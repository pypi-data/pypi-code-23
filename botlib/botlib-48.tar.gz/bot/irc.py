# BOTLIB - Framework to program bots !!
#
# irc.py (internet relay chat)
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
# 9-1-2018 As the creator of this file, I disclaim all rights on this file. 
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" irc bot. """

from bot import __version__
from bot import Bot
from bot.event import Event
from bot.obj import Config, Object
from bot.select import Select
from bot.thr import Launcher
from bot.users import Users
from bot.utils.decorators import get_args

import _thread
import logging
import os
import queue
import random
import re
import socket
import ssl
import time

class EDISCONNECT(Exception):

    """ the remote server disconnected. """

    pass

class ECHANNEL(Exception):

    """ wrong channel is provided. """

    pass

class IRC(Bot, Select):

    """ Bot to connect to IRC networks. """

    cc = "!"
    default = ""

    def __init__(self, *args, **kwargs):
        Bot.__init__(self, *args, **kwargs)
        Select.__init__(self)
        self._started = False
        self._buffer = []
        self._connected = Object()
        self._handlers.register("263", self.h263)
        self._handlers.register("315", self.h315)
        self._handlers.register("352", self.h352)
        self._handlers.register("353", self.h353)
        self._handlers.register("366", self.h366)
        self._handlers.register("376", self.connected)
        self._handlers.register("433", self.h433)
        self._handlers.register("ERROR", self.errored)
        self._handlers.register("MODE", self.moded)
        self._handlers.register("PING", self.pinged)
        self._handlers.register("PONG", self.ponged)
        self._handlers.register("QUIT", self.quited)
        self._handlers.register("INVITE", self.invited)
        self._handlers.register("PRIVMSG", self.privmsged)
        self._handlers.register("NOTICE", self.noticed)
        self._handlers.register("JOIN", self.joined)
        self._last = time.time()
        self._lastline = ""
        self._lock = _thread.allocate_lock()
        self._oldsock = None
        self._outqueue = queue.Queue()
        self._sock = None
        self._threaded = False
        self.encoding = "utf-8"

    def _bind(self, server, default="localhost"):
        """ find the internet adress of the IRC server (uses DNS). """
        try:
            self._oldsock.bind((server, 0))
        except socket.error:
            if not server:
                try:
                    socket.inet_pton(socket.AF_INET6, server)
                except socket.error:
                    pass
                else:
                    server = default
            if not server:
                try:
                    socket.inet_pton(socket.AF_INET, server)
                except socket.error:
                    pass
            if not server:
                ips = []
                try:
                    for item in socket.getaddrinfo(server, None):
                        if item[0] in [socket.AF_INET, socket.AF_INET6] and item[1] == socket.SOCK_STREAM:
                            ip = item[4][0]
                            if ip not in ips:
                                ips.append(ip)
                except socket.error:
                    pass
                else:
                    server = random.choice(ips)
        return server

    def _connect(self, nick, server, port=6667, ipv6=False):
        """ configure the IRC socket. """
        if ipv6:
            self._oldsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self._oldsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.blocking = True
        self._oldsock.setblocking(self.blocking)
        self._oldsock.settimeout(60.0)
        logging.warn("connect %s %s" % (server, port))
        self._oldsock.connect((server, port))
        self._oldsock.setblocking(self.blocking)
        self._oldsock.settimeout(700.0)
        if self.ssl:
            self._sock = ssl.wrap_socket(self._oldsock)
        else:
            self._sock = self._oldsock
        self.fsock = self._sock.makefile("r")
        self._resume.fd = self._sock.fileno()
        os.set_inheritable(self._resume.fd, os.O_RDWR)
        self.register_fd(self._resume.fd)
        self._connected.ready()

    def _output(self):
        """ output loop reading from _outqueue. """
        while not self._stopped:
            args = self._outqueue.get()
            if not args or self._stopped:
                break
            self.out(*args)
            
    def _some(self, ssl=False, encoding="utf-8"):
        """ read from socket, add to buffer and return last line. """
        try:
            if ssl:
                inbytes = self._sock.read()
            else:
                inbytes = self._sock.recv(512)
        except ConnectionResetError:
            raise EDISCONNECT()
        txt = str(inbytes, encoding)
        if txt == "":
            raise EDISCONNECT()
        self._lastline += txt
        splitted = self._lastline.split("\r\n")
        for s in splitted[:-1]:
            self._buffer.append(s)
            if not s.startswith("PING") and not s.startswith("PONG"):
                logging.warn("%s" % s.strip())
        self._lastline = splitted[-1]

    def announce(self, txt):
        """ announce txt to all joined channels. """
        for channel in self.channels:
            self._outqueue.put_nowait((channel, txt))

    def close(self):
        """ close the irc sockets, """
        if self.ssl:
            self.oldsock.shutdown(1)
            self.oldsock.close()
        else:
            self._sock.shutdown(1)
            self._sock.close()
        self.fsock.close()

    def connect(self, nick, server, port=6667):
        """ connect to server. """
        if not self._started:
            self.start()
        self._stopped = False
        self._connect(nick, server, port)
        self.nick = nick
        self.server = server
        self.logon(nick, server)

    def connected(self, event):
        """ called when the bot is connected. """
        self._connected.ready()
        if "servermodes" in self:
            self.raw("MODE %s %s" % (self.nick, self.servermodes))

    def dcced(self, event, s):
        """ DCC callback. Starts a DCC thread. """
        from .dcc import DCC
        lhr = Launcher()
        users = Users()
        if not users.allowed(event.origin, "DCC"):
            return
        s.send(bytes('Welcome to BOTLIB ' + event.nick + " !!\n", self.encoding))
        s.setblocking(True)
        os.set_inheritable(s.fileno(), os.O_RDWR)
        bot = DCC()
        bot.origin = event.origin
        lhr.launch(bot.start, s, event.origin)

    def dccconnect(self, event):
        """ connect to a DCC socket. """
        event.parse()
        addr = event._parsed.args[1]
        port = event._parsed.args[2][:-1]
        port = int(port)
        if re.search(':', addr):
            s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((addr, port))
        self.dcced(event, s)

    def dccresume(self):
        f = Fleet().load(os.path.join(workdir, "runtime", "fleet"))
        fleet = construct(f)
        for b in fleet.get_bots("dcc"):
            bot = construct(b)
            bot.start(bot._resume.fd2, bot._origin)

    def event(self):
        """ return an event from the buffer (if available). """
        self._connected.wait()
        if not self._buffer:
            self._some()
        line = self._buffer.pop(0)
        e = self.parsing(line.rstrip())
        e.bare = True
        return e

    def dispatch(self, event):
        """ function called to dispatch event to it's handler. """
        handlers = self._handlers.get(event.command, [])
        for handler in handlers:
            handler(event)

    def join(self, channel, password=""):
        """ join a channel. """
        if not channel:
            raise ECHANNEL(channel)
        if password:
            self.raw('JOIN %s %s' % (channel, password))
        else:
            self.raw('JOIN %s' % channel)
        if channel not in self.channels:
            self.channels.append(channel)

    def joinall(self):
        """ join all channels. """
        for channel in self.channels:
            self.join(channel)

    def logon(self, nick, server, username="bot", realname="bot"):
        """ logon to the IRC network. """
        self.raw("NICK %s" % nick)
        self.raw("USER %s %s %s :%s" % (username, server, server, realname))

    def out(self, channel, line):
        """ output method, split into 375 char lines, sleep 3 seconds. """
        line = str(line)
        for txt in line.split("\n"):
            if time.time() - self._last < 3.0:
                time.sleep(3.0)
            self.privmsg(channel, txt)

    def parsing(self, txt):
        """ parse txt line into an Event. """
        rawstr = str(txt)
        obj = Event()
        obj.txt = ""
        obj.cc = self.cc
        obj.arguments = []
        arguments = rawstr.split()
        obj.origin = arguments[0]
        if obj.origin.startswith(":"):
            obj.origin = obj.origin[1:]
            if len(arguments) > 1:
                obj.command = arguments[1]
            if len(arguments) > 2:
                txtlist = []
                adding = False
                for arg in arguments[2:]:
                    if arg.startswith(":"):
                        adding = True
                        txtlist.append(arg[1:])
                        continue
                    if adding:
                        txtlist.append(arg)
                    else:
                        obj.arguments.append(arg)
                    obj.txt = " ".join(txtlist)
        else:
            obj.command = obj.origin
            obj.origin = self.server
        try:
            obj.nick, obj.origin = obj.origin.split("!")
        except:
            pass
        if obj.arguments:
            obj.target = obj.arguments[-1]
        else:
            obj.target = "" 
        if obj.target.startswith("#"):
            obj.channel = obj.target
        else:
            obj.channel = obj.nick
        if not obj.txt and len(arguments) == 1:
            obj.txt = arguments[1]
        if not obj.txt:
            obj.txt = rawstr.split(":")[-1]
        obj.cb = obj.command
        obj.id = self.id
        obj.pure = True
        return obj

    def part(self, channel):
        """ leave a channel. """
        self.raw('PART %s' % channel)
        if channel in self.channels:
            self.channels.remove(channel)

    def raw(self, txt):
        """ output text to the IRC server. """
        if not txt.startswith("PING") and not txt.startswith("PONG"):
            logging.warn("%s" % txt)
        if not txt.endswith("\r\n"):
            txt += "\r\n"
        txt = txt[:512]
        txt = bytes(txt, "utf-8")
        self._last = time.time()
        try:
            self._sock.send(txt)
            return
        except (BrokenPipeError, ConnectionResetError):
            pass
        except AttributeError:
            try:
                self._sock.write(txt)
                return
            except (BrokenPipeError, ConnectionResetError):
                return

    def say(self, channel, txt, type="normal"):
        """ say txt on a channel. """
        self._outqueue.put_nowait((channel, txt))

    def start(self):
        """ start the IRC bot. """
        Bot.start(self)
        Select.start(self)
        lhr = Launcher()
        self._started = True
        self.walk("bot")
        lhr.launch(self._output)

    def stop(self):
        """ stop the IRC bot. """
        super().stop()
        self.quit("http://bitbucket.org/bthate/bot")
        self._stopped = True
        self._outqueue.put(None)
        self.ready()

    def noticed(self, event):
        """ called when the bot is being noticed. """
        pass

    ## callbacks

    def errored(self, event):
        """ error handler. """
        if "closed" in event.txt or "refused" in event.txt or "disconnect" in event.txt:
            self.reconnect()

    def invited(self, event):
        """ called when the bot is invited to a channel. """
        self.join(event.channel)

    def joined(self, event):
        """ called when someone joined a channel. """
        channel = event.txt.split()[0]
        logging.warn("joined %s" % channel)
        self.ready()

    def moded(self, event):
        """ MODE callback. """
        pass

    def pinged(self, event):
        """ ping callback. """
        self.pongcheck = True
        self.pong(event.txt)

    def ponged(self, event):
        """ pong callback. """
        self.pongcheck = False

    def quited(self, event):
        """ called when someone quits IRC. """
        logging.error("quit %s" % event.origin)

    def privmsged(self, event):
        """ PRIVMSG callback, forwards the event to the kernel for handling. """
        users = Users()
        event.parse()
        if event.txt.startswith("\001DCC"):
            self.dccconnect(event)
        elif event.txt.startswith("\001VERSION"):
            self.ctcpreply(event.nick, "VERSION BOTLIB #%s - http://bitbucket.org/bthate/bot" % __version__)
            return
        users._userhosts[event.nick] = event.origin
        event.pure = False
        super().dispatch(event)

    def ctcped(self, event):
        """ called when the bot is CTCP'ed. """
        pass

    def h001(self, event):
        """ 001 handler. """
        pass

    def h002(self, event):
        """ 002 handler. """
        pass

    def h003(self, event):
        """ 003 handler. """
        pass

    def h004(self, event):
        """ 004 handler. """
        self._connected.ready()
        pass

    def h005(self, event):
        """ 005 handler. """
        pass

    def h263(self, event):
        """ 263 handlers. """
        logging.error("h263 %s" % event)
        self.stop()

    def h315(self, event):
        """ 315 handler. """
        pass

    def h352(self, event):
        """ 352 handler. """
        users = Users()
        args = event.arguments
        users._userhosts[args[5]] = args[2] + "@" + args[3]

    def h353(self, event):
        """ 353 handler. """
        pass

    def h366(self, event):
        """ 366 handler. """
        pass

    def h433(self, event):
        """ 433 handler. """
        self.nick(event.target + "_")

    def h513(self, event):
        """ 513 PING response handler. """
        self.raw("PONG %s" % event.arguments[-1])

    def nick(self, nick):
        """ change nick of the bot. """
        self.raw('NICK %s' % nick[:16])
        
    ## RAW output

    def who(self, channel):
        """ send a WHO query. """
        self.raw('WHO %s' % channel)

    def names(self, channel):
        """ send a NAMES query. """
        self.raw('NAMES %s' % channel)

    def whois(self, nick):
        """ send a WHOIS query. """
        self.raw('WHOIS %s' % nick)

    def privmsg(self, channel, txt):
        """ send a PRIVMSG. """
        self.raw('PRIVMSG %s :%s' % (channel, txt.strip()))

    def voice(self, channel, nick):
        """ send a MODE +v. """
        self.raw('MODE %s +v %s' % (channel, nick))

    def doop(self, channel, nick):
        """ send a MODE +o. """
        self.raw('MODE %s +o %s' % (channel, nick))

    def delop(self, channel, nick):
        """ send a MODE -o. """
        self.raw('MODE %s -o %s' % (channel, nick))

    def quit(self, reason='http://bitbucket.com/bthate/bl'):
        """ send a QUIT message with a reason for quitting. """
        self.raw('QUIT :%s' % reason)

    def notice(self, channel, txt):
        """ send NOTICE to channel/nick. """
        self.raw('NOTICE %s :%s' % (channel, txt))

    def ctcp(self, nick, txt):
        """ send CTCP to nick. """
        self.raw("PRIVMSG %s :\001%s\001" % (nick, txt))

    def ctcpreply(self, channel, txt):
        """ send a NOTICE message in reply to a CTCP message. """
        self.raw("NOTICE %s :\001%s\001" % (channel, txt))

    def action(self, channel, txt):
        """ send a /me ACTION. """
        self.raw("PRIVMSG %s :\001ACTION %s\001" % (channel, txt))

    def getchannelmode(self, channel):
        """ query channel modes. """
        self.raw('MODE %s' % channel)

    def settopic(self, channel, txt):
        """ set topic on a channel. """
        self.raw('TOPIC %s :%s' % (channel, txt))

    def ping(self, txt):
        """ send PING. """
        self.raw('PING :%s' % txt)

    def pong(self, txt):
        """ send PONG. """
        self.raw('PONG :%s' % txt)
