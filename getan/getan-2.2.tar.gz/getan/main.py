#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) 2010 by Ingo Weinzierl <ingo.weinzierl@intevation.de>
# (c) 2011 by Björn Ricks <bjoern.ricks@intevation.de>
#
# A python worklog-alike to log what you have 'getan' (done).
#
# This is Free Software licensed under the terms of GPLv3 or later.
# For details see LICENSE coming with the source of 'getan'.
#

import logging
import os
import os.path

from optparse import OptionParser

import getan
import getan.config as config

from getan.backend import DEFAULT_DATABASE, Backend
from getan.controller import GetanController

logger = logging.getLogger()


def main():

    usage = "usage: %prog [options] [databasefile (default: " + \
        DEFAULT_DATABASE + ")]"
    version = "getan version %s" % getan.__version__
    parser = OptionParser(usage=usage, version=version)
    parser.add_option("--init-only", action="store_true", dest="initonly",
                      help="create databasefile if necessary and exit")
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      help="set verbosity to debug")
    parser.add_option("-l", "--logfile", dest="logfile", metavar="FILE",
                      help="write log information to FILE [default: %default]",
                      default="getan.log")
    (options, args) = parser.parse_args()
    logargs = dict()
    if options.debug:
        logargs["level"] = logging.DEBUG
    if options.logfile:
        logargs["filename"] = options.logfile
    config.initialize(**logargs)
    global logger

    if len(args) > 0:
        backend = Backend(args[0])
        logging.info("Using database '%s'." % args[0])
    else:
        if os.path.isfile(DEFAULT_DATABASE):
            database = os.path.abspath(DEFAULT_DATABASE)
        else:
            getan_dir = os.path.expanduser(os.path.join("~", ".getan"))
            if not os.path.exists(getan_dir):
                os.mkdir(getan_dir)
            database = os.path.join(getan_dir, DEFAULT_DATABASE)

        backend = Backend(database)
        logging.info("Using database '%s'." % database)

    if options.initonly:
        return

    controller = GetanController(backend)

    try:
        controller.main()
    except KeyboardInterrupt:
        pass
    finally:
        controller.shutdown()


if __name__ == '__main__':
    main()
