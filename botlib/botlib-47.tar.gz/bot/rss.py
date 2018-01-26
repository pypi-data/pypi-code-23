# BOTLIB - Framework to program bots !!
#
# bot/rss.py
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

""" rss module (needs feedparser). """

from bot.db import Db
from bot.clock import Repeater
from bot.obj import Config, Default, Object
from bot.register import Register
from bot.thr import Launcher
from bot.utils.time import ENODATE, file_time, to_time
from bot.utils.url import get_url, get_feed, strip_html


try:
    import feedparser
except:
    pass

import logging
import os
import urllib

db = Db()

seen = Object()
seen.urls = []

class Feed(Object):
    """ feed typed object. """
    pass

class Rss(Object):
    """ rss entry """
    pass

class Fetcher(Register):

    """ RSS class for fetching rss feeds. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sleep = kwargs.get("sleep", 600)
        self.display_list = []
        self.summary = []
        
    def display(self, obj):
        """ format feed items so that it can be displayed. """
        result = ""
        skip = False
        for key in self.display_list:
            if key == "summary":
                skip = True
                for k in self.summary:
                    if k in obj.link:
                        skip = False
                if skip:
                    continue
            data = obj.get(key, None)
            if data:
                result += "%s - " % strip_html(data.rstrip())
        if result:
            return result[:-3].rstrip()

    def fetch(self, obj):
        """ fetch a feed from provied obj (uses obj.rss as the url). """
        from bot.core import fleet
        nr = 0
        for o in list(get_feed(obj.rss))[::-1]:
            if o.link in seen.urls:
                continue
            seen.urls.append(o.link)
            nr += 1
            feed = Feed(o)
            for bot in fleet:
                txt = self.display(feed)
                if txt:
                    bot.announce(txt)
            feed.services = "rss"
            skip = False
            if skip:
                continue
            if "updated" in feed:
                try:
                    date = file_time(to_time(feed.updated))
                    feed.save(stime=date)
                    continue
                except ENODATE as ex:
                    logging.info("ENODATE %s" % str(ex))
            feed.save()
        return nr

    def run(self):
        """ find all rss object and fetch the corresponding feeds. """
        lhr = Launcher()
        res = []
        thrs = []
        nr = len(seen.urls)
        for obj in db.find("rss"):
            if "rss" not in obj:
                continue
            if not obj.rss:
                continue
            thr = lhr.launch(self.fetch, obj)
            thrs.append(thr)
        for thr in thrs:
            res.append(thr.join())
        seen.sync()
        logging.warn("fetched %s" % ",".join([str(x) for x in res]))
        return res

    def start(self, *args, **kwargs):
        """ start rss fetcher. """
        from obj import cfg
        lhr = Launcher()
        last = db.last("fetcher")
        if last:
            self.upgrade(last)
        if not self.display_list:
            self.display_list = ["title", "summary", "link"]
        seen.load(os.path.join(cfg.workdir, "runtime", "seen"))
        repeater = Repeater(600, self.run)
        lhr.launch(repeater.start)
        self.ready()
