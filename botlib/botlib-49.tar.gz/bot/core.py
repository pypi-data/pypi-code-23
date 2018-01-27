# BOTLIB - Framework to program bots !!
#
# bot/core.py
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

""" core module to stash runtime objects.. """

from bot.db import Db
from bot.fleet import Fleet
from bot.handler import Handler
from bot.loader import Loader
from bot.obj import Config, cfg
from bot.thr import Launcher
from bot.users import Users
from bot.utils.log import level
from bot.utils.shell import parse_cli

import bot.obj as obj

db = Db()
fleet = Fleet()
launcher = Launcher()
loader = Loader()
users = Users()

def start(workdir=""):
    cfg.update(parse_cli())
    cfg.workdir = obj.cfg.workdir or workdir
    if cfg.banner:
        print("%s %s\n" % (cfg.name,  __version__))
    if workdir or cfg.workdir:
        cfg.workdir = cfg.workdir or workdir
    if cfg.level:
        level(cfg.level, form="plain")
    loader.walk("bot")
    users.uber("root@shell")
    return cfg
    