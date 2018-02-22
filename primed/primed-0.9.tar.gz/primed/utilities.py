#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
  MMMMMMMMMNh  MMMMMMMMMNd  MMMM  MMMMm     MMMM  MMMMMMMMd  MMMMMMMMMN
  MMMMdhhMMMM  MMMMdhhMMMM  MMMM  MMMMMs   /MMMM  MMMMNmmmm  MMMMdhhMMMM
  MMMM   mMMM  MMMM   MMMM  MMMM  MMMMMM-.mMMMMM  MMMM       MMMM   MMMM
  MMMM   mMMM  MMMM   MMMM  MMMM  MMMMMMdsMMMMMM  MMMM       MMMM   MMMM
  MMMM   mMMM  MMMM   MMMM  MMMM  MMMMMMMMMMMMMM  MMMMNddd   MMMM   MMMM
  MMMM   mMMM  MMMMmdmMMMM  MMMM  MMMMdMMMMdMMMM  MMMMNddd   MMMM   MMMM
  MMMM   mMMM  MMMMdMMMMm   MMMM  MMMM/hMMN-MMMM  MMMM       MMMM   MMMM
  MMMM --NMMM  MMMM/ MMMm   MMMM  MMMM  NM  MMMM  MMMM       MMMM   MMMM
  MMMMNNNMMMM  MMMM  dMMM   MMMM  MMMM      MMMM  MMMMMNNNN  MMMMNNNMMMM
  MMMMdhhhhh   hhhh   hhhh  hhhh  hhhh      hhhh  hhhhhhhhs  hhhhhhhhhh
  MMMM
  MMMM
  MMMM
  MMMM
  KP:

########################################################################
#                                                                      #
#                            PRIMED TOOLKIT                            #
#                                                                      #
########################################################################
'''

__author__ = "Eugene Bann, Primed"
__copyright__ = 'Copyright (C) 2018 Demios, Inc.'
__version__ = '0.9'

colours = {
    'OK': '\033[92m',
    'INFO': '\033[94m',
    'WARN': '\033[93m',
    'ERROR': '\033[91m',
    'FATAL': '\033[31m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m',
    'END': '\033[0m'
}

def cprint(to_print, style=None, bold=False, underline=False, newline=True):
    end_char = "\n" if newline else ' '
    output = colours['BOLD'] if bold else ''
    output = output + colours['UNDERLINE'] if underline else output
    output = output + colours[style] if style in colours else output
    print(output + str(to_print) + colours['END'], end=end_char, flush=True)
