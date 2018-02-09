#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
/**
 *   Copyright (C) 2012-2017 Oslandia <infos@oslandia.com>
 *
 *   This library is free software; you can redistribute it and/or
 *   modify it under the terms of the GNU Library General Public
 *   License as published by the Free Software Foundation; either
 *   version 2 of the License, or (at your option) any later version.
 *   
 *   This library is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *   Library General Public License for more details.
 *   You should have received a copy of the GNU Library General Public
 *   License along with this library; if not, see <http://www.gnu.org/licenses/>.
 */
"""

import logging
from logging import StreamHandler
from gtfslib.dao import Dao
from dbtools import PsqlLoader
import re
import sys
import os

def parse_db_string(param):
    """
    Parse the parameter string as a PostgreSQL db connection string or an URI
    And return a pair of strings with both representations (db_string, db_uri)
    """
    if param.startswith("postgresql://"):
        # from uri to connection string
        from urlparse import urlparse
        p = urlparse(param)
        db_string = [('host', p.hostname),
                     ('port', str(p.port)),
                     ('username', p.username),
                     ('password', p.password),
                     ('dbname', p.path)]
        return (" ".join([k + "=" + v for k,v in db_string]), param)
    else:
        db_params = dict([(k,v.strip("'")) for k,v in re.findall(r"(\S+) *= *('.*?'|\S+)", param)])
        db_host = db_params.get("host") or ""
        db_port = ""
        if db_params.get("port"):
            db_port = db_port + ":" + db_params["port"]
        db_name = db_params.get("dbname") or ""
        host_port = db_host + db_port
        s = ''
        if db_params.get("username"):
            s = db_params["username"]
            if db_params.get("password"):
                s = s + ':' + db_params['password']
            s = s + "@"
        db_uri = "postgresql://" + s + host_port + "/" + db_name
        return (param, db_uri)

class GTFSPrimeImporter:
    def __init__(self, source = "", dbstring = "", logfile = None, pt_network = None):
        self.db_string, self.db_uri = parse_db_string(dbstring)
        self.source = source
        self.logfile = logfile
        self.pt_network = pt_network

    def load(self):
        print "DB params:", self.db_string
        print "DB URI:", self.db_uri
        logger = logging.getLogger('libgtfs')
        logger.setLevel(logging.INFO)
        logger.addHandler(StreamHandler(sys.stdout))
        dao = Dao(self.db_uri, sql_logging = self.logfile, schema="tempus_gtfs")

        dao.load_gtfs(self.source, feed_id=self.pt_network)

        loader = PsqlLoader(dbstring = self.db_string, logfile = self.logfile)
        loader.set_sqlfile(os.path.join(os.path.dirname(__file__), 'sql', 'gtfsp.sql'))
        return loader.load()

def list_gtfs_feeds(dbstring):
    db_string, db_uri = parse_db_string(dbstring)
    logger = logging.getLogger('libgtfs')
    logger.setLevel(logging.INFO)
    logger.addHandler(StreamHandler(sys.stdout))
    dao = Dao(db_uri, schema="tempus_gtfs")
    for feed in dao.feeds():
        print feed.feed_id if feed.feed_id != "" else "(default)"

def delete_gtfs_feed(dbstring, feed_id):
    db_string, db_uri = parse_db_string(dbstring)
    logger = logging.getLogger('libgtfs')
    logger.setLevel(logging.INFO)
    logger.addHandler(StreamHandler(sys.stdout))
    dao = Dao(db_uri, schema="tempus_gtfs")
    feed = dao.feed(feed_id)
    if not feed:
        sys.stderr.write("PT network {} does not exist in the database\n".format(feed_id))
        sys.exit(1)
    dao.delete_feed(feed_id)
    dao.commit()

