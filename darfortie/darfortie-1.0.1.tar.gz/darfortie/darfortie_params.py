# Script Name: darfortie.py
# Author: Ken Galle
# License: GPLv3
# Description: returns a dictionary of values to be used as parameters in the dar command:
#   dar_path : path and name to dar executable, optional, defaults to 'dar'
#   config : string, possibly None
#   prune : list of string, possibly empty
#   incremental : boolean
#   source_path : string
#   dest_path_and_base_name : string

import optparse
import logging

# Keep the dar switches explicitly on the dar command line instead of buried in variables.
# so the params{} dictionary is fine, but without putting in, e.g. -R, etc.

# provides:
#   config parameter string
#   prune parameter string
#   incremental boolean
def parse():
    log = logging.getLogger('darfortie_params')
    usageString = "usage: \n%prog [common-options] [backup-options] <source_path> <dest_path_and_base_name>\n"
                  # + \
                  # "%prog [common-options] [restore-options] <dar_path_and_base_name> <destination_path>"
    descriptionString = "A front-end for dar that supports incremental backups based on " + \
    "the existing backups found in the destination folder.  <source_path> is the " + \
    "root path to back up (dar -R).  <dest_path_and_base_name> is the dar base name.  This " + \
    "may include an optional path.  This program will supply date strings to the final " + \
    "name and dar itself will supply slice numbers to form the complete filename."
    epilogString = "Based on http://dar.linux.free.fr/doc/mini-howto/dar-differential-backup-mini-howto.en.html"
    p = optparse.OptionParser(usage=usageString, description=descriptionString, epilog=epilogString)

#common options

    # -d --dar: dar filespec --> dar_path
    p.add_option("-d", "--dar", action="store", dest="dar_path", metavar="dar_filespec",
        help="filespec of dar executable; defaults to 'dar'")

    # -c --config: specify .dar config file --> conf
    p.add_option("-c", "--config", action="store", dest="conf", metavar="config_filespec",
        help="filespec of dar config file to use instead of .darrc or etc/darrc.")

#backup options

    # -P --prune: add dar prune paths --> prune
    p.add_option("-P", "--prune", action="append", dest="prune", metavar="prune_path",
        help="Specify prune paths (dar -P) to add to call to dar. Paths should be relative to " +
        "<source_path>.  This option can be repeated as needed.")

    # -i --incremental: enable incremental (dar -A) mode
    p.add_option("-i", "--incremental", action="store_true", dest="incremental", default=False,
        help="search for previous backup to use for incremental backup (dar -A).  " +
        "Finds most recent like-named backup in destination path.")

    # -I --previous_path: path to location of previous file for use by incremental option
    p.add_option("-I", "--previous_path", action="store", dest="previous_path", metavar="previous_path",
        help="alters the behavior of --incremental such that the search for a previous " +
        "backup file is done in previous_path, instead of the destination path.")

#restore options  (need parse_args() grouping feature

    # dictionary to return
    params = {}

    # parse command line
    opts, args = p.parse_args()

    # Note optparse errors return exit code 2.

    if len(args) != 2:
        p.print_usage()
        exit(1)

    params['dar_path'] = opts.dar_path
    params['config'] = opts.conf
    params['prune'] = opts.prune
    params['incremental'] = opts.incremental
    params['previous_path'] = opts.previous_path
    params['source_path'] = args[0]
    params['dest_path_and_base_name'] = args[1]

    log.info("params:dar_path=" + str(params['dar_path']))
    log.info("params:config=" + str(params['config']))
    if params['prune'] is None:
        log.info("params:prune is None")
    else:
        log.info("params:prune count=" + str(len(params['prune'])))
        for onePath in params['prune']:
            log.info("params:prune=" + str(onePath))
    log.info("params:incremental=" + str(params['incremental']))
    log.info("params:source_path=" + str(params['source_path']))
    log.info("params:dest_path_and_base_name=" + str(params['dest_path_and_base_name']))
    log.info("params:previous_path=" + str(params['previous_path']))

    return params
