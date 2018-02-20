#!/usr/bin/python

# 	Author: Steven HK Wong
#	  Create Date: Sep 2014
#		Description: A useful logging class 


import sys, getopt
import os
from time import gmtime, localtime, strftime
import datetime

PROGNAME=os.path.basename(sys.argv[0])
LOGFILE = '/dev/stdout'
NONE = int('00000000',2)
INFO = int('00000001',2)
TRACE = int('00000010',2)
DEBUG_1 = int('00000100',2)
DEBUG_2 = int('00001100',2)
DEBUG_3 = int('00011100',2)
LEVEL_STR = { INFO:'info', TRACE:'trace', DEBUG_1:'debug1', DEBUG_2:'debug2', DEBUG_3:'debug3' }

API =  '\tlogger.init([file])\n\
\tlogger.status()\n\
\tlogger.usage()\n\
\tlogger.setNone()\n\
\tlogger.setInfo()\n\
\tlogger.setTrace()\n\
\tlogger.setDebug(level)\n\
\tlogger.setClass(class_list) - list may contain objects or names of classes\n\
\tlogger.log(level,msg)\n\
\tlogger.logc(class,level,msg)\n\
\tlogger.info(msg)\n\
\tlogger.infoc(class,msg)\n\
\tlogger.trace(msg)\n\
\tlogger.tracec(class,msg)\n\
\tlogger.debug(level,msg)\n\
\tlogger.debug1(msg)\n\
\tlogger.debug2(msg)\n\
\tlogger.debug3(msg)\n\
\tlogger.debugc(class,level,msg)\n\
\tlogger.debug1c(class,msg)\n\
\tlogger.debug2c(class,msg)\n\
\tlogger.debug3c(class,msg)\n'

classes = []
log_level = INFO
logfile = LOGFILE

fh = None

def init (lfile=''):
  global logfile
  global fh

  if lfile != '':
    logfile=lfile

  try:
    fh = open(logfile,'a')
  except IOError , e :
    print 'Error:' , e
    sys.exit(2)
  
  
def usage (prefix='', fileHandle=None):
	if fileHandle == None:
		print '%sUsage:%s [-f logfile|--file logfile] [-h]' % (prefix,PROGNAME)
		print ' - logfile defaults to stdout'
	else:
		fileHandle.write ( '%sUsage:%s [-f logfile|--file logfile] [-h]\n' % (prefix,PROGNAME) )
		fileHandle.write ( ' - logfile defaults to stdout\n' )
	status_api(fileHandle)


### Provides classes logging
#-----------------------------------------
def logc (theclass, param1, param2 = None):
  if not hasClass(theclass):
    return

  if param2 == None:
    msg = param1
    level = None
  else:
    level = param1
    msg = param2
  
  ts = strftime("%Y-%m-%d %H:%M:%S", localtime())
  if level == None:
    fh.write( '%s;%s;%s\n' % (ts, theclass.__class__.__name__, msg))
    fh.flush()
  else:
    if ok(level):
      fh.write( '%s;%s;%s;%s\n' % (ts, theclass.__class__.__name__, LEVEL_STR[level], msg))
      fh.flush()

def infoc(theclass,msg):
  logc (theclass,INFO,msg)

def tracec(theclass,msg):
  logc (theclass,TRACE,msg)

def debugc(theclass,param1,param2=None):
  if param2 == None:
    msg = param1
    level = DEBUG1
  else:
    msg = param2
    level = param1
  logc (theclass,level,msg)

def debug1c(theclass,msg):
  logc (theclass,DEBUG_1,msg)

def debug2c(theclass,msg):
  logc (theclass,DEBUG_2,msg)

def debug3c(theclass,msg):
  logc (theclass,DEBUG_3,msg)

def setClass (theclasses):
  global classes
  if theclasses != None:
    for c in theclasses:
			if isinstance(c,str):
				classes.append(c)
			else:
				classes.append(c.__class__.__name__)

def hasClass (theclass):
  if theclass != None:
    if theclass.__class__.__name__ in classes:
      return True;

  return False

### Provides plain logging
#-----------------------------------------
def log (param1, param2 = None):
  if param2 == None:
    msg = param1
    level = None
  else:
    level = param1
    msg = param2
  
  ts = strftime("%Y-%m-%d %H:%M:%S", localtime())
  if level == None:
    fh.write( '%s;%s\n' % (ts, msg))
    fh.flush()
  else:
    if ok(level):
      fh.write( '%s;%s;%s\n' % (ts, LEVEL_STR[level], msg))
      fh.flush()

def info(msg):
  log (INFO,msg)

def trace(msg):
  log (TRACE,msg)

def debug(param1,param2=None):
  # checks single param but single param has to be msg
  if param2 == None:
    level = DEBUG_1
    msg = param1
  else:
    level = param1
    msg = param2
  log (level,msg)

def debug1(msg):
  log (DEBUG_1,msg)

def debug2(msg):
  log (DEBUG_2,msg)

def debug3(msg):
  log (DEBUG_3,msg)

def quiet():
  global log_level 
  log_level = NONE

def setNone():
  quiet()

def setInfo(on=True):
  global log_level 
  if on:
    log_level = log_level | INFO
  else:
    log_level = log_level & ~INFO

def setTrace(on=True):
  global log_level 
  if on:
    log_level = log_level | TRACE
  else:
    log_level = log_level & ~TRACE

def setDebug(level=DEBUG_1):
  global log_level 
  log_level = log_level | level

def ok (level):
  level = int(level)
  if level & log_level == level:
    return True
  else: 
    return False

def status_api(fh=None):
	if fh != None:
		fh.write ('\tAPI: \n')
		fh.write(API)
	else:
		print  '\tAPI: '
		print '%s' % (API)

def status_usage():
	usage('',fh)

def status():
  fh.write ('logfile: %s\n' % (logfile))
  status_usage ()

def main(argv):
  lfile = ''
  try:
    opts, args = getopt.getopt(argv,"hf:",["file="])
  except getopt.GetoptError:
    usage('Error:')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      usage()
      sys.exit()
    elif opt in ("-f", "--file"):
      lfile = arg
  init (lfile)

  print 'Testing ..'
  print 'logfile is ', logfile
  if len(args) == 0:
    args = ['Test line']
  
  log ("\n")
  status ()

  log ("quiet level:")
  quiet()
  for arg in args:
    log (INFO,arg)
    log (TRACE,arg)
    debug (arg)
    log (DEBUG_3,arg)

  log ("\n")
  log ("info level:")
  setInfo()
  for arg in args:
    log (INFO,arg)
    log (TRACE,arg)
    debug (arg)
    log (DEBUG_2,arg)
    log (DEBUG_3,arg)
  
  log ("\n")
  log ("trace level:")
  setNone()
  setTrace()
  for arg in args:
    log (INFO,arg)
    log (TRACE,arg)
    debug (arg)
    log (DEBUG_2,arg)
    log (DEBUG_3,arg)

  log ("\n")
  log ("debug-1 level:")
  setNone()
  setDebug(DEBUG_1)
  for arg in args:
    log (INFO,arg)
    log (TRACE,arg)
    debug (arg)
    log (DEBUG_2,arg)
    log (DEBUG_3,arg)

  log ("\n")
  log ("debug-2 level:")
  setNone()
  setDebug(DEBUG_2)
  for arg in args:
    log (INFO,arg)
    log (TRACE,arg)
    debug (arg)
    log (DEBUG_2,arg)
    log (DEBUG_3,arg)

  log ("\n")
  log ("debug-3 + trace level:")
  setNone()
  setTrace()
  setDebug(DEBUG_3)
  for arg in args:
    log (INFO,arg)
    log (TRACE,arg)
    debug (arg)
    log (DEBUG_2,arg)
    log (DEBUG_3,arg)
  
  log ("\n")
  log ("Class A info level:")
  class A(object):
    def myprint(self, msg):
      logc (self, INFO, msg)
      logc (self, TRACE, msg)
      logc (self, DEBUG_1, msg)
      logc (self, DEBUG_2, msg)
      logc (self, DEBUG_3, msg)
  class B(object):
    def myprint(self, msg):
      logc (self, INFO, msg)
      logc (self, TRACE, msg)
      logc (self, DEBUG_1, msg)
      logc (self, DEBUG_2, msg)
      logc (self, DEBUG_3, msg)

  setClass ( [A()] )
  setNone()
  setInfo()
  a = A()
  b = B()
  for arg in args:
    a.myprint(arg)
    b.myprint(arg)
  
  log ("\n")
  log ("Class A and B info level:")
  setClass ( [A(), B()] )
  setNone()
  setInfo()
  for arg in args:
    a.myprint(arg)
    b.myprint(arg)

  log ("\n")
  log ("Class A and B info off , trace on:")
  setInfo(False)
  setTrace()
  for arg in args:
    a.myprint(arg)
    b.myprint(arg)


if __name__ == "__main__":
  # get argv[1] onwards 
  main(sys.argv[1:])

