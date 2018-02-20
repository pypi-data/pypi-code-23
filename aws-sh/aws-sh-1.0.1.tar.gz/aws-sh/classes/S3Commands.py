from threading import Thread
from time import gmtime, localtime, strftime
import time
import sys
import os

# directory containing customed modules:
#sys.path.insert(0,"/apps/lib/python")
import logger

COMMAND_SHELL = "python -m aws-cmd -m s3 "
bucket = ''
prefix = ''



class S3Commands():
    
    def __init__(self):
        logger.tracec(self,'S3Commands()')

    def process (self,cmd="", inbucket='', cwd = '', args = []):
        logger.tracec(self,'process(' + cmd + ',bucket=' + inbucket + ', cwd=' +cwd + ')')

        global bucket
        global prefix
        prefix = cwd

        bucket = inbucket
        if cmd == "ls":
          self.ls(args)
          return
        if cmd == "tree":
          self.tree(args)
          return
        if cmd == "get":
          self.get(args)
          return
        if cmd == "put":
          self.put(args)
          return
        if cmd == "rm":
          self.rm(args)
          return
        if cmd == "del":
          try:
            ans = raw_input('Confirm [N/y] ? ')
          except KeyboardInterrupt:
            return
          if ans == 'y':
            self.delete(args)
          return
        print "not implemented"

    def ls (self,args=''):
        logger.tracec(self, '  ls()')
        if bucket:
          thecmd = COMMAND_SHELL + ' -b ' + bucket  + ' -C ls '
        else:
          thecmd = COMMAND_SHELL + ' -C ls'
        if len(args) == 1 and prefix:
          runcmd = thecmd + ' -P ' + prefix + '/' 
          logger.tracec(self, '  running ' + runcmd)
          f = os.popen(runcmd)
          print '%s\n' % (f.read())
        else:
          for arg in args[1:]:
            if prefix:
              runcmd = thecmd + ' -P ' + prefix + '/' + arg
            else:
              runcmd = thecmd + ' -P ' + arg
            logger.tracec(self, '  running ' + runcmd)
            f = os.popen(runcmd)
            print '%s\n' % (f.read())

    def tree (self,args):
        logger.tracec(self, '  tree()')
        if bucket:
          thecmd = COMMAND_SHELL + ' -b ' + bucket  + ' -C tree '
        else:
          thecmd = COMMAND_SHELL + ' -C tree'
        if len(args) == 1:
          if prefix:
            thecmd = thecmd + ' -P ' + prefix + '/' 
          logger.tracec(self, '  running ' + thecmd)
          f = os.popen(thecmd)
          print '%s\n' % (f.read())
        else:
          for arg in args[1:]:
            if prefix:
              runcmd = thecmd + ' -P ' + prefix + '/' + arg
            else:
              runcmd = thecmd + ' -P ' + arg
            logger.tracec(self, '  running ' + runcmd)
            f = os.popen(runcmd)
            print '%s\n' % (f.read())

    def get (self,args):
        logger.tracec(self, '  get()')
        if bucket:
          thecmd = COMMAND_SHELL + ' -b ' + bucket  + ' -C get '
        else:
          thecmd = COMMAND_SHELL + ' -C tree'
        if len(args) != 3:
          print 'Error: Insufficient arguments!'
          logger.tracec(self, '  Error: Insuficient arguments ' )
          return
        if prefix:
          if args[1].startswith('/'):
            _src = args[1]
          else:
            _src = prefix + '/' + args[1]
        else:
            _src = args[1]
        _dest = args[2]
        thecmd = thecmd + ' -P ' + _src + ' -F ' + _dest
        logger.tracec(self, '  running ' + thecmd)
        f = os.popen(thecmd)
        print '%s\n' % (f.read())

    def put (self,args):
        logger.tracec(self, '  put()')
        if bucket:
          thecmd = COMMAND_SHELL + ' -b ' + bucket  + ' -C put '
        else:
          thecmd = COMMAND_SHELL + ' -C tree'
        if len(args) != 3:
          print 'Error: Insufficient arguments!'
          logger.tracec(self, '  Error: Insuficient arguments ' )
          return
        if prefix:
          if args[2].startswith('/'):
            _dest = args[2]
          else:
            _dest = prefix + '/' + args[1]
        else:
            _dest = args[2]
        _src = args[1]
        thecmd = thecmd + ' -F ' + _src + ' -P ' + _dest
        logger.tracec(self, '  running ' + thecmd)
        f = os.popen(thecmd)
        print '%s\n' % (f.read())

    def rm (self,args):
        logger.tracec(self, '  rm()')
        if bucket:
          thecmd = COMMAND_SHELL + ' -b ' + bucket  + ' -C rm '
        else:
          thecmd = COMMAND_SHELL + ' -C tree'
        if len(args) < 2:
          print 'Error: Insufficient arguments!'
          logger.tracec(self, '  Error: Insuficient arguments ' )
          return
        for o in args[1:]:
          if prefix:
            rmcmd = thecmd + ' -P ' + prefix + '/' + o
          else:
            rmcmd = thecmd + ' -P ' + o
          logger.tracec(self, '  running ' + rmcmd)
          f = os.popen(rmcmd)
          print '%s\n' % (f.read())

    def delete (self,args):
        logger.tracec(self, '  del()')
        if bucket:
          thecmd = COMMAND_SHELL + ' -C del -f -b '
        else:
          thecmd = COMMAND_SHELL + ' -C tree'
        if len(args) < 2:
          print 'Error: Insufficient arguments!'
          logger.tracec(self, '  Error: Insuficient arguments ' )
          return
        for o in args[1:]:
          delcmd = thecmd + o
          logger.tracec(self, '  running ' + delcmd)
          print 'Deleting bucket ' + o + ' ... '
          f = os.popen(delcmd)
          print '%s\n' % (f.read())
            
            






    

