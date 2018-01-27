# BOTLIB - Framework to program bots !!
#
# bot/utils/shell.py
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

""" shell related functionality. """

import atexit
import logging
import optparse
import os
import readline
import rlcompleter
import stat
import sys
import termios

dirmask = 0o700
filemask = 0o600
histfile = os.path.join(os.path.expanduser("~"), ".bot_history")
resume = {}

opts_defs_sed = []

opts_defs = [
    ('-a', '--all', 'store_true', False, 'all', "init all modules"),
    ('-b', '--banner', 'store_true', False, 'banner', "show banner"),
    ("-c", "--channel", "string", "", "channel", "channel to join"),
    ('-d', '--workdir', 'string', os.path.abspath(os.path.join(os.path.expanduser("~"),".bot")), "workdir", "set working directory"),
    ('-g', '--global', 'store_true', False, 'usehomedir', "set working directory to ~/.bot"),
    ('-l', '--level', 'string', "error", 'level', "loglevel."),
    ('-i', '--init', 'string', '', 'init', "initialize (start) an module."),
    ('-n', '--nick', 'string', '', 'nick', "nick to use in channels."),
    ('-p', '--port', 'string', 6667, 'port', "port to run HTTP server on."),
    ('-r', '--room', 'string', "", 'room', "xmpp room to join."),
    ('-s', '--server', 'string', '', 'server', "server to connect to."),
    ('-u', '--user', 'string', '', 'user', 'JID to login on XMPP server'),
    ('-v', '--verbose', 'store_true', False, 'verbose', 'use verbose mode.'),
    ('-w', '--write', 'store_true', False, 'write', 'save kernel state after boot.'),
    ('-x', '--start', 'string', "", 'start', "start modules on boot."),
    ('-z', '--shell', 'store_true', False, 'shell', "enable shell cli."),
    ('-6', '--use_ipv6', 'store_true', False, 'use_ipv6', 'enable ipv6'),
    ('', '--completion', "store_true", False, 'completion', "use extended tab completion"),
    ('', '--creator', 'string', "Bart Thate", "creator", "the bot's creator's name."),
    ('', '--daemon', 'store_true', False, "daemon", "switch to daemon mode."),
    ('', '--description', 'string', "Framework to program bots", "description", "the bot's description."),
    ('', '--eggs', 'store_true', False, 'eggs', "load eggs located in the current working directory."),
    ('', '--license', 'store_true', False, 'license', 'show license.'),
    ('', '--homedir', 'string', os.path.abspath(os.path.expanduser("~")), "homedir", "homedir to use."),
    ('', '--name', 'string', "BOTLIB", "name", "the bot's name."),
    ('', '--reboot', 'store_true', False, 'reboot', "enable rebooting."),
    ('', '--resume', 'store_true', False, 'resume', "resume the bot."),
]

def make_opts(options, args=None, usage="bot [options]", version="none"):
    """" create options to check when command line is parsed. """
    parser = optparse.OptionParser(usage=usage, version=version)
    for option in options:
        optiontype, default, dest, helptype = option[2:]
        if "store" in optiontype:
            try:
                parser.add_option(option[0], option[1], action=optiontype, default=default, dest=dest, help=helptype)
            except Exception as ex:
                logging.error("%s option %s" % (str(ex), option))
                continue
        else:
            try:
                parser.add_option(option[0], option[1], type=optiontype, default=default, dest=dest, help=helptype)
            except Exception as ex:
                logging.error("^%s option %s" % (str(ex), option))
                continue
    if args:
        args = parser.parse_args(args)
    else:
        args = parser.parse_args(args)
    return args

def parse_cli(*args, **kwargs):
    """ parse the command line options. """
    opts, arguments = make_opts(opts_defs)
    cfg = {}
    cfg["args"] = arguments
    cfg.update(vars(opts))
    return cfg

def cdir(path):
    """ create a directory. """
    res = ""
    for p in path.split(os.sep):
        res += "%s%s" % (p, os.sep)
        padje = os.path.abspath(os.path.normpath(res))
        try:
            os.mkdir(padje)
        except (IsADirectoryError, NotADirectoryError, FileExistsError):
            pass
        except OSError as ex:
            logging.error(get_exception())
    return True

def termsetup(fd):
    """ preserve the old terminal attributes. """
    old = termios.tcgetattr(fd)
    return old

def termreset(fd, old):
    """ reset the terminale to previous serssion attributes. """
    termios.tcsetattr(fd, termios.TCSADRAIN, old)

class Completer(rlcompleter.Completer):

    """ Completer class used to complete bot commands. """

    def __init__(self, options):
        super().__init__()
        self.options = options

    def complete(self, text, state):
        """ the complete function itself. """
        if state == 0:
            if text:
                self.matches = [s for s in self.options if s and s.startswith(text)]
            else:
                self.matches = self.options[:]
        try:
            return self.matches[state]
        except IndexError:
            return None

def set_completer(optionlist):
    """ set the completer as part of readline functionality. """
    readline.parse_and_bind("tab: complete")
    completer = Completer(optionlist)
    readline.set_completer(completer.complete)
    atexit.register(lambda: readline.set_completer(None))

def enable_history():
    """ enable history written to file. """
    if not os.path.exists(histfile):
        d, f = os.path.split(histfile)
        cdir(d)
        touch(histfile)
    readline.read_history_file(histfile)
    atexit.register(close_history)

def close_history():
    """ write the command history to file. """
    readline.write_history_file(histfile)

def reset():
    """ reset the terminal. """
    close_history()
    if "old" in resume:
        termreset(resume["fd"], resume["old"])

def startup():
    """ function to call on startup of the program, preserving previous terminal settings. """
    global resume
    enable_history()
    resume["fd"] = sys.stdin.fileno()
    resume["old"] = termsetup(sys.stdin.fileno())
    atexit.register(reset)

def make_opts(options, args=None, usage="bot [options]", version="none"):
    """" create options to check when command line is parsed. """
    parser = optparse.OptionParser(usage=usage, version=version)
    for option in options:
        optiontype, default, dest, helptype = option[2:]
        if "store" in optiontype:
            try:
                parser.add_option(option[0], option[1], action=optiontype, default=default, dest=dest, help=helptype)
            except Exception as ex:
                logging.error("%s option %s" % (str(ex), option))
                continue
        else:
            try:
                parser.add_option(option[0], option[1], type=optiontype, default=default, dest=dest, help=helptype)
            except Exception as ex:
                logging.error("^%s option %s" % (str(ex), option))
                continue
    if args:
        args = parser.parse_args(args)
    else:
        args = parser.parse_args(args)
    return args

def reboot():
    """ perform a reboot. """
    os.execl(sys.argv[0], *(sys.argv + ["-r", "-z"]))

def check_permissions(p, dirmask=dirmask, filemask=filemask):
    """ set permission of the data dir to 0x700 or use provided dirmask/filemask. """
    uid = os.getuid()
    gid = os.getgid()
    try:
        stats = os.stat(p)
    except FileNotFoundError:
        return
    except OSError:
        d, fn = os.path.split(p)
        cdir(d)
        stats = os.stat(d)
    if stats.st_uid != uid:
        os.chown(p, uid, gid)
    if os.path.isfile(p):
        mask = filemask
    else:
        mask = dirmask
    m = oct(stat.S_IMODE(stats.st_mode))
    if m != oct(mask):
        os.chmod(p, mask)

def touch(fname):
    """ touch a file. """
    try:
        fd = os.open(fname, os.O_RDONLY | os.O_CREAT)
        os.close(fd)
    except TypeError:
        pass
    except Exception as ex:
        logging.error(get_exception())
