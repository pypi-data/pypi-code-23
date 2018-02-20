#!/bin/python
###################################################################
#
#   Author: Steven HK Wong
#   Created:  9 Oct 2017 
#   Version:  0.1
#
###################################################################
DEBUG = False
TRACE = True
HISTORY_FILE="~/.ashell.history"
#HISTORY_SIZE=100
HISTORY_SIZE=-1
VERSION="1.0"
AMI="ami-57dd3635"

import urllib2 as _urllib2
#import functools as _functools
import time 
import datetime
#import nltk 
#import lxml.html
from time import gmtime, localtime, strftime
import datetime
import os
#import thread
from threading import Thread
from classes import S3Commands, Ec2Commands, logger
from boto3 import *
import signal
import getopt
import sys
import logging

plog = logging.getLogger ( __name__ )


#####################################
# Support given below - DO NOT CHANGE
#####################################

#import logger
try:
  import readline
except ImportError:
  readline = None


LOG='/tmp/aws.log'
quit = False
mode = 'cmd'
context = 'ec2'
id = ''
HEADLESS = False
USAGE = False
histfile = None

DEFAULT_PROFILE =  ''
profile = DEFAULT_PROFILE
tags = ''
display_tags = ''
cwd = ''
bucket = ''

ec2 = Ec2Commands.Ec2Commands()
s3 = S3Commands.S3Commands()

# signal handlers
def signal_term_handler(signal, frame):
    print 'got SIGTERM'
    sys.exit(0)
 
def init_history():
  global histfile
  try:
    histfile = os.path.expanduser(HISTORY_FILE)
    if readline and os.path.exists(histfile):
#      readline.parse_and_bind('tab: complete') 
      readline.read_history_file(histfile)
  except Exception, e:
    print "Error opening " + HISTORY_FILE
    sys.exit(0)

def show_history (inlast=''):
  if not readline:
    return
  _len = readline.get_current_history_length()
  if not inlast:
    last = 10000;
  else:
    last = int(inlast)

  if last < 0:
    readline.clear_history()
    return

  i = _len - last 
  if i < 0:
    i = 1
  while i < _len:
    print readline.get_history_item(i)
    i += 1

def save_history():
  if readline:
    readline.set_history_length(HISTORY_SIZE)
    readline.write_history_file(histfile)


def usage(prefix=None):
  print ' -h,--help '
  print ' -H,--headless '
  print ' =============='
  print ' Interactive: '
  print ' h|help|?  - this help '
  print ' v         - show version'
  print ' q|quit    - quit '
  print ' debug     - toggle debug on/off'
  print ' trace     - toggle trace on/off'
  print ' ec2       - ec2 mode [default]'
  print ' s3        - s3 mode '
  print ' p         - sets profile'
  print ' cp        - clears profile'
  print ' log       - set log file (current: ' + LOG + ')'
  print ' history   - show command history Eg. history 5 - last 5 commands, history -1 clears all history'
  print ' status, s - show status'
  print ' ! command - run any os commands/scripts'
  print ' --- ec2 commands ------'
  print ' a         - Ami. Default: ' + AMI + ' Eg. a ami-6acfd409'
  print ' t         - enter tags.          Eg. t Name:AA user:BB'
  print ' ct        - clear tags.         ' 
  print ' dt        - display tags - only show these tags     ' 
  print ' ls        - list tagged instances'
  print ' start     - start instance.      Eg. start i-0adcd6fbd97418a07'
  print ' stop      - stop instance.       Eg. stop i-0adcd6fbd97418a07'
  print ' terminate - terminate instance.  Eg. terminate i-0adcd6fbd97418a07'
  print ' launch    - launch new instances.Eg. launch  1'
  print ' --- s3 commands ------'
  print ' bucket    - select bucket'
  print ' cd        - change directory     Nb. cd without argument clears it'
  print ' pwd       - show current directory'
  print ' tree      - show subtrees '
  print ' get       - download a s3 object'
  print ' put       - upload a s3 object'
  print ' rm        - remove a s3 object'
  print ' del       - delete a s3 bucket'

def ts ():
  ts = strftime("%Y-%m-%d %H:%M:%S", localtime())
  return ts

def clear_profile ():
  global profile
  profile = ''

def get_profile ():
  global profile
  if "AWS_PROFILE" in os.environ:
    profile = os.environ["AWS_PROFILE"] 

def set_profile ():
  if profile:
    os.environ["AWS_PROFILE"] = profile

def clear_tags ():
  global tags
  tags = ''

def get_tags (intags=[]):
  logger.trace('get_tags()')
  global tags
  if not intags:
    return tags
  _tags_str = ''
  for t in intags[1:]:
    if _tags_str:
      _tags_str = _tags_str + ',' + t
    else:
      _tags_str = t
  if _tags_str:
    return _tags_str

def get_dtags (intags=[]):
  logger.trace('get_dtags()')
  global display_tags
  if not intags:
    return 
  _tags_str = ''
  for t in intags[1:]:
    if _tags_str:
      _tags_str = _tags_str + ',' + t
    else:
      _tags_str = t
  if _tags_str:
    display_tags = _tags_str


def doOs (cmd_args):
    if len(cmd_args) < 1:
      return
    thecmd = ' '.join(cmd_args[1:])
    f = os.popen(thecmd)
    print '%s\n' % (f.read())

def doQuit ():
  global notdone
  global quit
  save_history()
  print 'Exiting ...'
  logger.info("Exiting .. ")
  exit(0)

def doStatus ():
  logger.info("doStatus()")
  print 'status: '
  print   '  profile - ' + profile
  print   '  log - ' + LOG
  print   '  AMI - ' + AMI
  if context == 'ec2':
    print '  tags - ' + tags
  if context == 's3':
    print '  bucket - ' + bucket
    print '  dir - ' + cwd
  if DEBUG:
    print '  debug on'
  else:
    print '  debug off'
  if TRACE:
    print '  trace on'
  else:
    print '  trace off'


def debugToggle():
  global DEBUG
  if DEBUG == True:
    DEBUG = False
    logger.setDebug(False)
    print 'debug off'
  else:
    DEBUG = True 
    logger.setDebug()
    print 'debug on'

def traceToggle():
  global TRACE
  if TRACE == True:
    TRACE = False
    logger.setTrace(False)
    print 'trace off'
  else:
    TRACE = True 
    logger.setTrace()
    print 'trace on'

def init_log ():
    logger.init(LOG)

def init_plog ():
    global plog
    hdlr = logging.FileHandler('/tmp/myapp.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    plog.addHandler(hdlr) 
    plog.setLevel(logging.ERROR)
    plog.setLevel(logging.WARNING)
    plog.setLevel(logging.DEBUG)
    plog.setLevel(logging.INFO)

def init():
    signal.signal(signal.SIGTERM, signal_term_handler)
    get_profile()
    init_history()
    init_log()
    logger.setTrace()
    logger.info('Inited ')
    logger.setClass ([ec2,s3])
    init_plog()
    plog.info("Started")

def interact():
    global server_thread
    global quit
    global mode
    global context
    global id
    global profile
    global tags
    global display_tags
    global bucket
    global cwd
    global LOG
    global AMI

    init()
    notdone = True
#   logger.setInfo()
    logger.info('Started ')
    while notdone :
      if mode == 'cmd':
        if profile:
          prompt = "<" + profile + "> (" + context +") : "
        else:
          prompt = "<-> (" + context +") : "
      if mode == 'talk':
        prompt = ""

      set_profile()
      
      try:
        cmd = raw_input(prompt)
      except KeyboardInterrupt:
        cmd = 'q'
      cmd_args = cmd.split();
      cmd = cmd.strip()
      logger.debug ( '%s %s' % ('cmd_args: ',  cmd_args ) )

      if cmd == 'status' or cmd == 's':
        doStatus ()
        continue
      if cmd != '' and cmd != None:
        if cmd_args[0] == 'talk':
          mode = 'talk'
          if len(cmd_args) > 1:
            id = cmd_args[1]
            continue
          continue
      if cmd == 's3':
        context = 's3'
        continue
      if cmd == 'ec2':
        context = 'ec2'
        continue
      if cmd == 'cp':
        clear_profile()
        continue
      if cmd and cmd_args[0] == 'log':
        if len(cmd_args) > 1:
          LOG = cmd_args[1]
          init_log()
          continue
      if cmd and cmd_args[0] == 'p':
        if len(cmd_args) > 1:
          profile = cmd_args[1]
          continue
      if cmd and cmd_args[0] == 'bucket':
        if len(cmd_args) > 1:
          bucket = cmd_args[1]
          continue
      if cmd and cmd_args[0] == 'pwd':
        if context == 's3':
          print cwd
          continue
      if cmd and cmd_args[0] == 'cd':
        if len(cmd_args) > 1:
          if not cwd:
            cwd = cmd_args[1]
          else:
            if cmd_args[1].startswith('/'):
              cwd = cmd_args[1]
            else:
              cwd = cwd + '/' + cmd_args[1]
          continue
        else:
          cwd = ''
          continue
      if cmd == 'ct':
        clear_tags()
        continue
      if cmd and cmd_args[0] == 'a':
        if len(cmd_args) > 1:
          AMI = cmd_args[1]
          continue
      if cmd and cmd_args[0] == 't':
        if len(cmd_args) > 1:
          tags = get_tags( cmd_args )
          continue
      if cmd and cmd_args[0] == 'dt':
        if len(cmd_args) > 1:
          get_dtags( cmd_args )
          continue
        else:
          display_tags = ''
      if cmd == 'q' or cmd == 'quit':
        notdone = False
        break
      if cmd == 'help' or cmd == 'h' or cmd == '?':
        usage()
        continue
      if cmd == 'v':
        print 'Version: ' + VERSION
        continue
      if cmd == 'debug':
        debugToggle()
        continue
      if cmd == 'trace':
        traceToggle()
        continue


      if len(cmd_args) == 0:
        continue

      if cmd_args[0] == 'history':
        if len(cmd_args) > 1:
          show_history(cmd_args[1])
        else:
          show_history()
        continue

      if cmd_args[0] == 'status':
        doStatus ()
        continue

      if cmd_args[0] == '!':
        doOs (cmd_args)
        continue

      if context == 'ec2':
        ec2.process( cmd_args[0] , cmd_args, tags, display_tags, DEBUG, AMI)
        continue

      if context == 's3':
        s3.process( cmd_args[0] , bucket, cwd, cmd_args )
        continue


      print "Invalid command: " + cmd

    doQuit()

def  getopts():
  global USAGE
  global HEADLESS

  try:
    opts, args = getopt.getopt(sys.argv[1:],"hH",["help","headless"])
  except getopt.GetoptError:
    usage('Error:')
    sys.exit(2)
  for opt, arg in opts:
    if opt in ('-h', "--help"):
      USAGE = True
    if opt in ('-H', '--headless'):
      HEADLESS = True

def main ():
  getopts()

  if USAGE:
    usage()

  if HEADLESS:
    print "running headless .."
  else:
    interact()

if __name__ == '__main__':
  main()
