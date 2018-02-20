from threading import Thread
from time import gmtime, localtime, strftime
import time
import sys
import os
#from boto3 import *

# directory containing customed modules:
#sys.path.insert(0,"/apps/lib/python")
import logger

COMMAND_SHELL = "python -m aws-cmd"
MAX_LAUNCH = 2





class Ec2Commands():
    
    def __init__(self):
        logger.tracec(self,'Ec2Commands()')

    def process (self,cmd="", args = [], tags='', display_tags='', debug=False, ami=''):
        logger.tracec(self,'process(' + cmd + ')')
        if cmd == "ls":
          self.ls(args,tags,display_tags, debug)  
        if cmd == "start":
          self.start(args,tags)  
        if cmd == "stop":
          self.stop(args,tags)  
        if cmd == "terminate":
          self.terminate(args,tags)  
        if cmd == "launch":
          self.launch(args,tags,ami)  
      
    def ls (self,args,tags, display_tags,debug=False):
        logger.tracec(self, '  ls()')
        if display_tags:
          _dtags = '--ft=' + display_tags
        else:
          _dtags = ''
        if tags:
            _tags = '-t ' + tags
        else:
            _tags = ''
        thecmd = COMMAND_SHELL + ' ' + _tags + ' ' + _dtags
        if 'ip' in args:
          thecmd = thecmd + ' -I'
        if debug:
          print 'Command: ' + thecmd
        logger.tracec(self, '  running ' + thecmd)
        f = os.popen(thecmd)
        print '%s\n' % (f.read())

    # Don't allow bulk stop, too risky in production environment!!
    def start (self,args,tags):
        logger.tracec(self, '  start()')
        _tags = ''
#        if tags:
#            _tags = '-t ' + tags
#        else:
#            _tags = ''
        thecmd = COMMAND_SHELL + '  -C start ' + _tags
        for arg  in args[1:]:
          thecmd = thecmd + ' -i ' + arg
        logger.tracec(self, '  running ' + thecmd)
        f = os.popen(thecmd)
        print '%s\n' % (f.read())

    # Don't allow bulk stop, too risky in production environment!!
    def stop (self,args,tags):
        logger.tracec(self, '  stop()')
        _tags = ''
#        if tags:
#            _tags = '-t ' + tags
#        else:
#            _tags = ''
        thecmd = COMMAND_SHELL + ' -C stop ' + _tags
        for arg  in args[1:]:
          thecmd = thecmd + ' -i ' + arg
        logger.tracec(self, '  running ' + thecmd)
        f = os.popen(thecmd)
        print '%s\n' % (f.read())

    # Don't allow bulk terminate, too risky in production environment!!
    def terminate (self,args,tags):
        logger.tracec(self, '  terminate()')
        _tags = ''
#        if tags:
#            _tags = '-t ' + tags
#        else:
#            _tags = ''
        thecmd = COMMAND_SHELL + ' -C terminate ' + _tags
        for arg  in args[1:]:
          thecmd = thecmd + ' -i ' + arg
        logger.tracec(self, '  running ' + thecmd)
        f = os.popen(thecmd)
        print '%s\n' % (f.read())


    # Don't allow bulk launch, too risky in production environment!!
    def launch (self,args,tags,ami=''):
        logger.tracec(self, '  launch()')
        _tags = ''
#        if tags:
#            _tags = '-t ' + tags
#        else:
#            _tags = ''
        _errmsg = ''
        thecmd = COMMAND_SHELL + ' -C launch ' + _tags
        for arg  in args[1:]:
          if int(arg) > MAX_LAUNCH: 
            _errmsg = 'Launching >= ' + str(MAX_LAUNCH) + ' instances not allowed'
            print '%s\n' % (_errmsg)
            return
          thecmd = thecmd + ' -q ' + arg
        if ami != '':
          thecmd = thecmd + ' -a ' + ami
        logger.tracec(self, '  running ' + thecmd)
        f = os.popen(thecmd)
        print '%s\n' % (f.read())





    

