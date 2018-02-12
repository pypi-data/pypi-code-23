#-*-coding:iso-8859-1-*-
#!/logiciels/public/bin/python-2.4
#
""" this module handles all file functions"""

import re
import os, shutil
import stat
from messages import WARNING, signal,\
     get_flag, MSG, send_message
import time
from env import MY_MACHINE_FULL_NAME

EMPTY_DICT = {}



############################################################################
#                         
# FONCTION FICHIERS 
#                         
############################################################################
#
#
#    
def grep(motif, file_name, col = None, error_type = WARNING):
    """
     Fonction qui cherche la premiere ligne contenant un motif dans un fichier
     et renvoie le contenu d'une colonne de cette ligne
     
     fic             --> Nom du fichier
     motif         --> Motif a chercher
     col             --> La liste des Numeros de colonne a extraire
     endroit     --> Un objet de type situation
     
     Renvoie la colonne col et un indicateur indiquant si le motif a y trouver

     """
    #
    trouve = -1
    motif0 = str.replace(motif,    '\\MOT',    '[^\s]*')
    motif0 = str.replace(motif0,    '\\SPC',    '\s*')

    # col can be    Nothing,         one figure,     or    a list of figures
    type_matching = "Columns"
    if col == None:
        type_matching = "Grep"
    if type(col) == type(2):
        col = [col] 
    if type(col) == type("chaine"):
        type_matching = "Regexp"
        masque0 = str.replace(col,    '\\MOT',    '[^\s]*')
        masque0 = str.replace(masque0,    '\\SPC',    '\s*')

    try:
        file_name_full_path = MY_MACHINE_FULL_NAME+":"+os.getcwd()
    except:
        file_name_full_path = MY_MACHINE_FULL_NAME+":??????:%s"%get_flag('my_job')

    if os.path.isfile(file_name)==False:
        if col == None:
            signal(error_type, "file '%s' read \n\t from path '%s' \
                                                \n\t searched for motif '%s' does not exist!!!!"\
                         %(file_name, file_name_full_path, motif))
        else:
            signal(error_type, "file '%s' read \n\t from path '%s' \
                                                \n\t searched for motif '%s' to get column # %s \
                                                \n\t  file does not exist!!!"\
                         %(file_name, file_name_full_path, motif, col))
        return None
    else:
        file_scanned = open(file_name, "r")
        for ligne in file_scanned.readlines():
            if (len(ligne) >= 1):
                if (re.search(motif0, ligne)):
                    trouve = 1
                    if type_matching == "Columns":
                        file_scanned.close()
                        colonnes = str.split(ligne)
                        col_out = []
                        for i in col:
                            col_out.append(colonnes[i])
                        if len(col_out) == 1:
                            return col_out[0]
                        else:
                            return col_out
                        break
                    elif type_matching == "Grep":
                        file_scanned.close()
                        return ligne[:-1]    
                    elif type_matching == "Regexp":
                        matched = re.search(masque0, ligne, re.VERBOSE)
                        if matched:
                            file_scanned.close()
                            return matched.groups()
        file_scanned.close()

        if (trouve == -1):
            if col == None:
                signal(error_type, "file '%s' \
                             \n\t searched for motif '%s'    : no matching found!!!!"\
                             %(file_name_full_path, motif))
            else:
                signal(error_type, "file '%s' \
                             \n\t searched for motif '%s' to get column # %s : no matching found!!!!"\
                             %(file_name_full_path, motif, col))
            return None

    return None



def greps(motif, file_name, col = None, error_type = WARNING):
    """
     Fonction qui retourne toute ligne contenant un motif dans un fichier
     et renvoie le contenu d'une colonne de cette ligne
     
     fic             --> Nom du fichier
     motif         --> Motif a chercher
     col             --> La liste des Numeros de colonne a extraire
     endroit     --> Un objet de type situation
     
     Renvoie la colonne col et un indicateur indiquant si le motif a y trouver

     """
    #
    if get_flag('debug'):
        print "greps called for searching %s in %s " % (motif, file_name)

    
    trouve = -1
    rep = []
    motif0 = str.replace(motif,    '\\MOT',    '[^\s]*')
    motif0 = str.replace(motif0,    '\\SPC',    '\s*')

    # col can be    Nothing,         one figure,     or    a list of figures
    type_matching = "Columns"
    if col == None:
        type_matching = "Grep"
    if type(col) == type(2):
        col = [col] 
    if type(col) == type("chaine"):
        type_matching = "Regexp"
        masque0 = str.replace(col,    '\\MOT',    '[^\s]*')
        masque0 = str.replace(masque0,    '\\SPC',    '\s*')

    file_name_full_path = MY_MACHINE_FULL_NAME+":"+os.getcwd()

    if os.path.isfile(file_name)==False:
        if col == None:
            signal(error_type, "file '%s' read \n\t from path '%s' \
                                                \n\t searched for motif '%s' does not exist!!!!"\
                         %(file_name, file_name_full_path, motif))
        else:
            signal(error_type, "file '%s' read \n\t from path '%s' \
                                                \n\t searched for motif '%s' to get column # %s \
                                                \n\t  file does not exist!!!"\
                         %(file_name, file_name_full_path, motif, col))
        return None
    else:
        file_scanned = open(file_name, "r")
        for ligne in file_scanned.readlines():
            if get_flag('debug'):
                print ligne,motif0
            if (len(ligne) >= 1):
                if (re.search(motif0, ligne)):
                    trouve = 1
                    if type_matching == "Columns":
                        file_scanned.close()
                        colonnes = str.split(ligne)
                        col_out = []
                        for i in col:
                            col_out.append(colonnes[i])
                        if len(col_out) == 1:
                            rep.append(col_out[0])
                            continue
                        else:
                            rep.append(col_out)
                            continue
                        break
                    elif type_matching == "Grep":
                        file_scanned.close()
                        rep.append(ligne[:-1])
                        continue
                    elif type_matching == "Regexp":
                        matched = re.search(masque0, ligne, re.VERBOSE)
                        if matched:
                            file_scanned.close()
                            rep.append(matched.groups())
                            continue
        file_scanned.close()

        if (trouve == -1):
            if col == None:
                signal(error_type, "file '%s' \
                             \n\t searched for motif '%s'    : no matching found!!!!"\
                             %(file_name_full_path, motif))
            else:
                signal(error_type, "file '%s' \
                             \n\t searched for motif '%s' to get column # %s : no matching found!!!!"\
                             %(file_name_full_path, motif, col))
            return None

    return rep


################################################################################
# portalocker.py - Cross-platform (posix/nt) API for flock-style file locking.
#                  Requires python 1.5.2 or better.
################################################################################
"""Cross-platform (posix/nt) API for flock-style file locking.

Synopsis:

   import portalocker
   file = open("somefile", "r+")
   portalocker.lock(file, portalocker.LOCK_EX)
   file.seek(12)
   file.write("foo")
   file.close()

If you know what you're doing, you may choose to

   portalocker.unlock(file)

before closing the file, but why?

Methods:

   lock( file, flags )
   unlock( file )

Constants:

   LOCK_EX
   LOCK_SH
   LOCK_NB

Exceptions:

    LockException

Notes:

For the 'nt' platform, this module requires the Python Extensions for Windows.
Be aware that this may not work as expected on Windows 95/98/ME.

History:

I learned the win32 technique for locking files from sample code
provided by John Nielsen <nielsenjf@my-deja.com> in the documentation
that accompanies the win32 modules.

Author: Jonathan Feinberg <jdf@pobox.com>,
        Lowell Alleman <lalleman@mfps.com>
Version: $Id: portalocker.py 5474 2008-05-16 20:53:50Z lowell $

"""



import os

class LockException(Exception):
    # Error codes:
    LOCK_FAILED = 1

if os.name == 'nt':
    import win32con
    import win32file
    import pywintypes
    LOCK_EX = win32con.LOCKFILE_EXCLUSIVE_LOCK
    LOCK_SH = 0 # the default
    LOCK_NB = win32con.LOCKFILE_FAIL_IMMEDIATELY
    # is there any reason not to reuse the following structure?
    __overlapped = pywintypes.OVERLAPPED()
elif os.name == 'posix':
    import fcntl
    LOCK_EX = fcntl.LOCK_EX
    LOCK_SH = fcntl.LOCK_SH
    LOCK_NB = fcntl.LOCK_NB
else:
    raise RuntimeError, "PortaLocker only defined for nt and posix platforms"

if os.name == 'nt':
    def lock(file, flags):
        hfile = win32file._get_osfhandle(file.fileno())
        try:
            win32file.LockFileEx(hfile, flags, 0, -0x10000, __overlapped)
        except pywintypes.error, exc_value:
            # error: (33, 'LockFileEx', 'The process cannot access the file because another process has locked a portion of the file.')
            if exc_value[0] == 33:
                raise LockException(LockException.LOCK_FAILED, exc_value[2])
            else:
                # Q:  Are there exceptions/codes we should be dealing with here?
                raise
    
    def unlock(file):
        hfile = win32file._get_osfhandle(file.fileno())
        try:
            win32file.UnlockFileEx(hfile, 0, -0x10000, __overlapped)
        except pywintypes.error, exc_value:
            if exc_value[0] == 158:
                # error: (158, 'UnlockFileEx', 'The segment is already unlocked.')
                # To match the 'posix' implementation, silently ignore this error
                pass
            else:
                # Q:  Are there exceptions/codes we should be dealing with here?
                raise

elif os.name == 'posix':
    def lock(file, flags):
        try:
            fcntl.flock(file.fileno(), flags)
        except IOError, exc_value:
            #  IOError: [Errno 11] Resource temporarily unavailable
            if exc_value[0] == 11:
                raise LockException(LockException.LOCK_FAILED, exc_value[1])
            else:
                raise
    
    def unlock(file):
        fcntl.flock(file.fileno(), fcntl.LOCK_UN)


#############################################################################
# Single Identification 
#   - get_checksum_id
#############################################################################
#

def get_checksum_id(description,results_dir):

    st = "Description=%s,results_dir=%s" % \
         (description,results_dir)
    chksum = reduce(lambda x,y:x+y, map(ord, st))
    if get_flag('debug'):
        print "chksum=%s for st=%s " % (st,chksum)
    return chksum

def get_timestamp():
    timestamp = "%s"%time.time()
    if get_flag('debug'):
        print "timestamp=%s" % (timestamp)
    return timestamp




#############################################################################
# Installation procedure
#   - Checksum
#   - diff and copy
#############################################################################
#
    

def checksum(dir,checksum_saved=None):

    if get_flag("running_directory"):
        out_checksum = "%s/.out_checksum"%get_flag("running_directory")
    else:
        out_checksum = "/tmp/.out_checksum_%s"%get_flag('user_name')

    if checksum_saved:
        out_checksum=checksum_saved
        
    cmd = "cd %s; find  . -type f -exec cksum {} \; > %s "%(dir,out_checksum)
    if get_flag('debug'):
        print cmd
    os.system(cmd)

    f_out=open(out_checksum,"r")
    res = f_out.readlines()
    f_out.close()

    if get_flag('debug'):
        print "checksum obtained in %s :\n"%dir,res[:10]
        
    return res

    

def synchronize_orig_tmp(dir_to_sync):

    need_to_install = False
    to_copy = []
    dirs = list(dir_to_sync)


    already_installed_touched_file = '/tmp/%s/MAESTRO_Jobs/installed_%s_%s.txt' % \
        (get_flag('user_name'),get_flag('checksum_id'),get_flag('timestamp'))

    
    # checking installation
    if get_flag('my_job') >0:
        if get_flag('debug'):
            print "checking for %s"%already_installed_touched_file

        if os.path.isfile(already_installed_touched_file):
            if get_flag("my_job")>0:
                send_message("status","%05d : Installation already ...OK for /%s@%s:"
                             % (get_flag("my_job"),
                                get_flag('user_name'),
                                MY_MACHINE_FULL_NAME), "G")
            return

    if get_flag("my_job")>0:
        send_message("status","%05d : Installation Checking on /%s@%s:"
             % (get_flag("my_job"),
                get_flag('user_name'),
                MY_MACHINE_FULL_NAME), "G")

    k=0
    dirs = list(dir_to_sync)

    if True:
      tmpdir = '/tmp/%s/MAESTRO_Jobs' % (get_flag('user_name'))
      try:
        if not(os.path.isdir(tmpdir)):
            # result directory does not exists anyway!
            os.makedirs(tmpdir)
      except:
          pass

      # taking the lock
      install_lock = open('%s/install_lock_%s_%s.txt' % \
                              (tmpdir,get_flag('checksum_id'),
                               get_flag('timestamp')),
                          "a+")
      lock(install_lock, LOCK_EX)

      # checking if installation has not been done meanwhile
      if os.path.isfile(already_installed_touched_file):
          send_message("status","%05d : Installation already ...OK for /%s@%s:"
                        % (get_flag("my_job"),
                           get_flag('user_name'),
                           MY_MACHINE_FULL_NAME), "G")
          if get_flag("debug"):
              print "already installed %s"%already_installed_touched_file
          install_lock.close()
          return


      timestamp = "Installation at %s for my_job=%s\n" % (MY_MACHINE_FULL_NAME,get_flag("my_job"))
      install_lock.write( timestamp )
      

      dirs = list(dir_to_sync)


      # I am the one on the node installing everything
      if get_flag("my_job")>0:
          send_message("status","%05d : Installation Ongoing for /%s@%s:"
                       % (get_flag("my_job"),
                          get_flag('user_name'),
                          MY_MACHINE_FULL_NAME), "G")
              
      while (dirs):
        src_dir = dirs.pop(0)
        dst_dir = dirs.pop(0)

        # syncing tmp and original directories ...
        command="mkdir -p %s; rsync -avz %s %s >> %s/LOGS/install.%s.log 2>&1  "%\
            (dst_dir,src_dir,dst_dir,MSG.results_directory,get_flag("my_job"))
#         command="mkdir -p %s mkdir -p %s; rsync -avz %s %s >> %s/install.log 2>&1  "%\
#             (get_flag("running_directory"),
#              dst_dir,src_dir,dst_dir,get_flag("running_directory"))
        #command="mkdir -p %s; rsync -avz %s %s >> install.log 2>&1 "%(dst_dir,src_dir,dst_dir)
        if get_flag("debug"):
            print command
        os.system(command)


      # touching a file to state installation has been done
      if get_flag("debug"):        
          print "writting %s"%already_installed_touched_file
      fic = open(already_installed_touched_file,"w")
      fic.write("installation ok")
      fic.close()
      if get_flag("debug"):        
          print "written %s"%already_installed_touched_file

      install_lock.close()
      if get_flag("debug"):        
          print "releasing lock!"
      #die
      
    if get_flag("my_job")>0:
           send_message("status","%05d : Installation ...OK for /%s@%s:"
             % (get_flag("my_job"),
                get_flag('user_name'),
                MY_MACHINE_FULL_NAME), "G")


if __name__ == "__main__":
    r=checksum("maestro")
    print r
    

if __name__ == '__main__':
    from time import time, strftime, localtime
    import sys
    import portalocker

    log = open('log.txt', "a+")
    portalocker.lock(log, portalocker.LOCK_EX)

    timestamp = strftime("%m/%d/%Y %H:%M:%S\n", localtime(time()))
    log.write( timestamp )

    print "Wrote lines. Hit enter to release lock."
    dummy = sys.stdin.readline()

    log.close()




