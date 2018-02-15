#!/usr/bin/env python3

'''
A simple script to generate a local bib file from a central
database so that only items actually cited appear.
'''

import os
import sys

from pybtex.__main__ import main as run_bibtex
from pybtex import auxfile
from pybtex import database

DEFAULT_CFG = {
    'db': '~/.makebib/db.bib'
}
CFG_FILES = ['/etc/makebib', '~/.makebib', './.makebib']


HELP = """
A simple script to generate a local bib file from a central database.

Usage: """+sys.argv[0]+""" arg

  arg is

    either the basename of a texfile, in which case
    the script creates a bib file and populates it with items
    which are cited by the document and can be found in the
    central database. Then it runs (a python version) of bibtex
    on the texfile.

    or --list which is followed by one of cited, missing, all, cfg
    and a texfile in which case the program prints out a list of

      cited    citekeys which are cited in the texfile

      missing  citekeys which are cited in the texfile but not present
               in the central database

      all      all citekeys in the central database

      cfg      configuration


CONFIGURATION

  The program reads its configuration from """+', '.join(CFG_FILES)+""".
  Each configuration option is given on a single line in the form of

        key = val

  Spaces around '=' are ignored as is everything following the first '#'.
  Lines not containing '=' are also ignored. The options are case-insensitive.
  Currently the following options (and their default values) are available:

"""+'\n'.join(["        " + k + " = " + v for k, v in DEFAULT_CFG.items()])


def make_bib(basename, bib_dbase):
    aux_data = auxfile.parse_file(basename + '.aux')
    db = database.parse_file(os.path.expanduser(bib_dbase))
    outdb = database.BibliographyData({key: db.entries[key] for key in aux_data.citations if key in db.entries})
    outdb.to_file(aux_data.data[0] + '.bib', bib_format='bibtex')


def list_cited_keys(basename):
    aux_data = auxfile.parse_file(basename + '.aux')
    print('\n'.join(aux_data.citations))


def list_db_keys(bib_dbase):
    db = database.parse_file(os.path.expanduser(bib_dbase))
    print('\n'.join(db.entries.keys()))


def list_missing_keys(basename, bib_dbase):
    aux_data = auxfile.parse_file(basename + '.aux')
    db = database.parse_file(os.path.expanduser(bib_dbase))
    missing = [key for key in aux_data.citations if key not in db.entries]
    print('\n'.join(missing))


def load_cfg():
    global CFG_FILES, DEFAULT_CFG
    cfg = {}
    for k, v in DEFAULT_CFG.items():
        cfg[k] = v
    for f in CFG_FILES:
        f = os.path.expanduser(f)
        if os.path.exists(f):
            with open(f, 'r') as IN:
                for ln in IN.readlines():
                    comment_pos = ln.find('#')
                    if comment_pos > -1:
                        ln = ln[:comment_pos]
                    try:
                        key, val = ln.split('=')
                        key = key.strip().lower()
                        val = val.strip()
                        if len(key) > 0:
                            cfg[key] = val
                    except:
                        pass
    return cfg

if __name__ == '__main__':
    CFG = load_cfg()
    if len(sys.argv) < 2:
        print(sys.argv[0]+": Needs at least one argument")
        sys.exit(1)
    if sys.argv[1] == '--list':
        if sys.argv[2] == 'cited':
            list_cited_keys(sys.argv[3])
        elif sys.argv[2] == 'missing':
            list_missing_keys(sys.argv[3], CFG['db'])
        elif sys.argv[2] == 'all':
            list_db_keys(CFG['db'])
        elif sys.argv[2] == 'cfg':
            for k, v in CFG.items():
                print(k, '=', v)
    elif sys.argv[1] == '--help':
        print(HELP)
    else:
        make_bib(sys.argv[1], CFG['db'])
        run_bibtex()

