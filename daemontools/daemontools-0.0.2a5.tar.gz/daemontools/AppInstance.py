#!/usr/bin/env python

'''
Module for previous instance detection.
Author: Lubos Medovarsky, lubos@medovarsky.com, 2008
Copyright: LGPLv3
'''
from __future__ import print_function
import os
import os.path
import sys
import time

def touch(fname):
    try:
        os.utime(fname, None)
    except OSError:
        open(fname, 'a').close()

class ApplicationInstance:
    '''class used to handle one application instance mechanism'''
    pid_file = None

    def __init__(self, pid_file):
        '''specify the file used to save the application instance pid'''
        self.pid_file = pid_file
        self.check()

    def check(self):
        '''check if the current application is already running'''
        '''check if the pidfile exists'''
        try:
            print('trying to create pid file {}...'.format(self.pid_file))
            touch(self.pid_file)
            if not os.path.isfile(self.pid_file):
                print("Cannot create file {}.".format(self.pid_file))
                sys.exit(1)
            print('success')
        except:
            print("error touching file")
            sys.exit(1)
        '''read the pid from the file'''
        pid = 0
        try:
            fd = open(self.pid_file, 'rt')
            data = fd.read()
            fd.close()
            pid = int(data)
        except:
            pass
        '''check if the process with specified by pid exists'''
        if 0 == pid:
             return
        try: #flock(pidfile)?
            os.kill(pid, 0) #this will raise an exception if the pid is not valid
        except:
            return
        '''exit the application'''
        print("The application is already running !")
        exit(0) #exit raise an exception so don't put it in a try/except block
        #return True

    def startApplication(self):
        '''called when the single instance starts to save it's pid'''
        fh = open(self.pid_file, 'wt')
        fh.write(str(os.getpid()))
        fh.close()

    def exitApplication(self):
        '''called when the single instance exit (remove pid file)'''
        try:
            os.remove(self.pid_file)
        except:
            pass

if __name__ == '__main__':
    '''create application instance'''
    appInstance = ApplicationInstance('/tmp/AppInstance.pid')
    '''do something here'''
    print("Test only: pretending as running for a moment...")
    time.sleep(3)
    '''remove pid file'''
    appInstance.exitApplication()
    '''finished.'''
