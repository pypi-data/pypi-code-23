""" maestro module """


# duplicata de la sortie standard et erreur dans un fichier
# dump final fait a la fin de save_results_and_clean dans job

import sys
import os

class Tee(object):
    def __init__(self,name,stream):
        self.terminal = stream
        self.logfilename = os.getcwd()+"/%s.dat"%name
        self.log = open(self.logfilename, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.log.flush()

    def dump(self,target):
        self.log.flush()
        #print "DUMPING ......."+self.logfilename
        #os.system("ls -l %s"%self.logfilename)
        #self.log.close()
        shutil.copy(self.logfilename,target)
        self.log.close()
        self.log = open(self.logfilename, "w")
            
sys.stdout = Tee("stdout",sys.stdout)
sys.stderr = Tee("stderr",sys.stderr)


from messages import *
from fichiers import *
from calcul import *
from job import *
from config import *

from env import MY_MACHINE



