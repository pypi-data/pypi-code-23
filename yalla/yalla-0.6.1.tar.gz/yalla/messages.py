#-*-coding:iso-8859-1-*-
#!/logiciels/public/bin/python-2.4

"""
module handling signals, timers, message logging to
local and distant log system
"""


import sys, os,  time
import exceptions, traceback



import copy

import logging, logging.handlers

from env import MY_MACHINE, MY_MACHINE_FULL_NAME, TMPDIR



#####################################################################
#
# Constants
#
#####################################################################

JOIN_SEPARATOR1 = "--/--"

# error types

ERROR = "err"
CRITICAL = "critical"
WARNING = "warning"
INFO = "info"
LOG_FILENAME = "maestro.log"





#####################################################################
#
# Global variables stored in a Singleton
#
#####################################################################
#
# -- IMPORTANT REMARK --
#
# Forcing the gathering of global varirable in this Singleton 
#         will ease the distribution
#         of the environment in a future version of maestro 
#
#####################################################################
#

class Singleton:
    """
    Singleton class to garantee only one occurrence of object
    """
    def __init__(self):
        # variable related to T�s  (class TimerClass)
        self.duree = {}
        self.timer_on = {}
        self.time_start = {}
        self.current_job = None

GV = Singleton()


#############################################################################
# class timerCenter managing timers
#############################################################################
#

class Timer:
    """
    timer class to handle time measurements
    """
    def __init__(self, timer_name = "Principal"):
        self.timer_name = timer_name
        GV.duree[timer_name] = 0
        GV.timer_on[timer_name] = False
        
    def start(self):
        """
        starting timer
        """
        GV.timer_on[self.timer_name] = True
        GV.time_start[self.timer_name] = time.gmtime()          
    
    def stop(self):
        """
        stopping accounting time for this timer
        """
        if GV.timer_on[self.timer_name]:
            GV.timer_on[self.timer_name] = False
            tfin  =  time.gmtime()
            GV.duree[self.timer_name] = \
                GV.duree[self.timer_name]\
                + time.mktime(tfin) \
                - time.mktime(GV.time_start[self.timer_name])

    def clear(self):
        """
        reset to zero the time measured by this timer
        """
        GV.timer_on[self.timer_name] = False
        GV.time_start[self.timer_name] = 0

    def duree(self):
        """
        return duration mesared by this timer
        """
        return GV.duree[self.timer_name]


class MyError(Exception):
    """
    class reporting maestro own formatted error message
    """
    def __init__(self, value):
        send_message("logger", "Exit", "G")
        self.value  =  value
    def __str__(self):
        return repr(self.value)
    

class MyErrorNoExit(Exception):
    """
    class reporting maestro own formatted error message
    """
    def __init__(self, value):
        self.value  =  value
    def __str__(self):
        return repr(self.value)
    

class my_local_logger:

    def __init__(self, name, log_file_name):
        log_file_name = str.replace(log_file_name, '//', '/')
        self.fic = open(log_file_name, "w")

    def info(self,message):
        self.fic.write(message+"\n")
                        
    def flush(self):
        self.fic.flush()
                        

#############################################################################
# class MessageCenter managing signals, messages, stacks, tracking, Exceptions
#############################################################################
#


class MessageCenter:
    """
    class managing messages
    """
    def __init__(self):

        self.level_stack = 3
        self.stacks = {"stack":["root"], "info":[], "contexte":[]}
        self.flags = {}
        self.tabs = {}
        self.tags = {}
        self.tags_balises = {}
        self.balises = {}

        self.streams = \
            {"stderr":sys.stderr, "stdout":sys.stdout, 
             "err":sys.stderr, "std":sys.stdout}
        self.stream_flusher = {}
        
        self.created_files = {}
        
        self.maestro_directory = os.getcwd()
        # fixing home bug on rendvous
        self.maestro_directory = \
            str.replace(self.maestro_directory, "home02", "home")


        if sys.platform  ==  "win32":
            cmd = "USERNAME"
        elif sys.platform  ==  "linux2":
            cmd = "USER"
        user_name = os.getenv(cmd) #or os.environ[cmd]
	self.set_flag('user_name',user_name)
    
    
        self.working_directory = \
            str.replace("%s/%s/MAESTRO_Jobs/" % (TMPDIR, user_name),
                        "//","/")
            
        self.set_flag("maestro_directory", self.maestro_directory)
        self.set_flag("working_directory", self.working_directory)


        self.results_directory  =  "unset yet"
        self.killing_filename   =  "unset yet"

        
        self.logging_setup()
        
        

    #########################################################################
    # Logger management
    #########################################################################
    


    def logging_setup(self):
        """ prepare logging environment"""
        #####################################################################
        #
        # Logging Setup
        #
        #####################################################################
        
        
        #--------------------------------------------------------------------
        # definition of local logger... dumping to file
        #--------------------------------------------------------------------
        local_logger  =  logging.getLogger('local')
        local_logger.setLevel(logging.INFO)
        
        # # Add the log message handler to the logger
        # ch  =  logging.handlers.RotatingFileHandler(
        #       'local.log', maxBytes = 200000, backupCount = 5)
        
        # #ch  =  logging.StreamHandler()
        # #ch.setLevel(logging.DEBUG)
        # # create formatter
        # formatter  =  logging.Formatter("%(asctime)s - %(message)s")
        # # add formatter to ch
        # ch.setFormatter(formatter)
        # # add ch to logger
        # local_logger.addHandler(ch)
        
        #self.main_logger = self.distant_logger('maestro',
        #     get_flag("logger_name", None), 
        #     get_flag("logger_port", None))

    #----------------------------------------------------------------------
    # definition of specific logger : local and global
    #----------------------------------------------------------------------
    
    def local_logger(self, name, log_file_name):
        """ make connection with a local logger """    
        new_logger = logging.getLogger("%s" % name)
        new_logger.propagate = 0

        log_file_name = str.replace(log_file_name, '//', '/')

        open(log_file_name, "w").close()
        
        handler  =  logging.handlers.RotatingFileHandler(
              log_file_name, maxBytes = 20000000, backupCount = 5)
    
        formatter  =  logging.Formatter("%(message)s")
        # add formatter to handler
        handler.setFormatter(formatter)
        # add handler to logger
        new_logger.addHandler(handler)
        return new_logger, handler
    
    def distant_logger(self, name, logger_name, 
                       logger_port, mode):
        """ make connection with a distant logger """
        #------------------------------------------------------------------
        # definition of global logger... dumping to server
        #------------------------------------------------------------------
        mode_and_name = "%s:-:%s" % (mode, name)
        global_logger = logging.getLogger('%s'%mode_and_name)
        global_logger.setLevel(logging.DEBUG)
        global_logger.propagate = 0
#        print mode_and_name
#        socketHandler  =  
#                logging.handlers.SocketHandler(mode_and_name, 
#                                               logger_port)
#        
        socket_handler = logging.handlers.SocketHandler(logger_name,
                                                        logger_port)
        # don't bother with a formatter, since a socket handler 
        # sends the event as an unformatted pickle
        global_logger.addHandler(socket_handler)
            
        return global_logger


    #########################################################################
    # tag management to save and retrieve a stack and info environment
    #########################################################################
    
    def save_env(self, tag_name):
        """ 
        save current state of the environnement 
        and associates it with a tag
        """
        self.tags[tag_name] = {}
        self.tags_balises[tag_name] = {}
        for stack in self.stacks.keys():
            self.tags[tag_name][stack] = \
                                       JOIN_SEPARATOR1.join(self.stacks[stack])
        self.tags_balises[tag_name] = copy.deepcopy(self.balises)
        
    def load_env(self, tag_name):
        """
        retrieve the state of the environment
        associated to a tag
        """
        if not tag_name in self.tags.keys():
            signal(ERROR, "Tries to goto tag '%s' that does not exist"%tag_name)
        for stack in self.stacks.keys():
            if stack in self.tags[tag_name].keys():  
                self.stacks[stack] = \
                    str.split(self.tags[tag_name][stack], JOIN_SEPARATOR1)
            else:
                del self.stacks[stack]
        self.balises = copy.deepcopy(self.tags_balises[tag_name])

            

    
    #########################################################################
    # message stack management
    #########################################################################
    
    def stack_add(self, stack, message):
        """ adding a message on the top of a stack"""
        if not (stack in self.stacks.keys()):
            self.stacks[stack] = []
        
        self.stacks[stack].append(message)
        


    #########################################################################
    # log management either local of global (if --logto argument is set)
    #########################################################################

    def send_message(self, stream, message, mode = "w"):
        """ process messages sent to the framework"""

        # "G" in mode  --> global shared logfile
        # "a" in mode  --> logfile continues and is not erased at each run

        if not (stream in self.streams.keys()):
            # log file has not been opened yet... let's proceed
            
            if mode.find("G") == -1 or \
               (not(get_flag("logger_name"))):
                description = get_flag("job_description")
                what = str.replace(description, " ", "_")
                running_directory = get_flag("running_directory")
                fic = "%s/%s.log" % \
                      (running_directory,  stream)
                #send_message("debug", "on %s fic =%s"%(MY_MACHINE_FULL_NAME,fic), "G")

                # removing previous logfile if not in appended mode
                fic = str.replace(fic, "//", "/")
                if os.path.isfile(fic) and not mode.find("a") == -1:
                    os.remove(fic)
                    
                # dumping on local file
                #self.streams[stream], self.stream_flusher[stream] = \
                #    self.local_logger(stream, fic)
                self.streams[stream]=self.stream_flusher[stream] = \
                    my_local_logger(stream, fic)
                self.created_files[fic] = 1
                if get_flag('debug'):
                    print "[LOG]\tlocal logger == %s == created " % stream
            else:
                # dumping through distant logfile
                self.streams[stream] = \
                    self.distant_logger(stream, 
                                        get_flag("logger_name", None), 
                                        get_flag("logger_port", None), 
                                        mode)
                if get_flag('debug'):
                    print "[LOG]\tdistant logger == %s == created " % stream

        if stream in ["std", "err", "stdout", "stderr", "error"]:    
            print >> self.streams[stream], message
            self.streams[stream].flush()
        else:
            if get_flag('debug'):
                print "[LOG]\tsend of a global msg to stream=%s\
                           \n \t through logger at  name=%s, port=%s, mode=%s\
                           \n \t message = '%s'" %\
                           (stream, 
                            get_flag("logger_name", None), 
                            get_flag("logger_port", None), 
                            mode,message)
            self.streams[stream].info(message)
            if mode.find("G") == -1:
                self.stream_flusher[stream].flush()



    #########################################################################
    # signal management
    #########################################################################

    def signal(self, signal_type, message, *args):
        """ sends a signal to framework """
        
        if signal_type == None:
            return

        if not(signal_type in [ERROR, INFO, WARNING, CRITICAL]):
            self.signal(ERROR, "type of signal unsupported %s"%signal_type)
    
        
        complete_message ="\n\n%s\n %s ERROR occured on \
                   \n\t machine: %s\
                   \n\t contexte: %s\
                   \n\t error:%s\n%s\n\n" % \
                   ("v"*80, signal_type,
                    MY_MACHINE_FULL_NAME,
                    get_flag('contexte',None),
                    message, "^"*80) 
        
        #self.send_message("stderr", complete_message, *args)


        
        if signal_type == ERROR:
            #send_message("status", "%05d : Done --> status=ERROR = %s" % (get_flag("my_job"),message), "G")
            raise MyError(complete_message)
        
        if signal_type == CRITICAL:
#           raise Exception(message)
            # taking the results back
            # send_message("logger", "CRITICAL %s" % (get_flag("my_job"), "G")
            #GV.current_job.save_results(take_all=True)
             
            set_flag("pinging", False)
            if not get_flag("no_stop_on_break"):
                
                # stopping the logger
                #send_message("status", "%05d : Done  --> status=CRITICAL = %s" % (get_flag("my_job"),message), "G")

                #send_message("logger", "Exit", "G")
                raise Exception(complete_message)
            else:
                send_message("std",
                             "Bye bye, be back anytime to check status!")
                sys.exit(0)

    #########################################################################
    # management of balises
    #########################################################################

    def set_balise(self, key, val):
        """
        assigns a value to the balise 'key'
        """
        self.balises[key] = val
        
    def get_balise(self, key, error_type = WARNING):
        """
        get the value stored in the balise 'key'
        """
        if not(key in self.balises.keys()):
            self.signal(error_type, "%s flag not initialized yet!!!"%key)
            return None
        return self.balises[key]


    #########################################################################
    # management of flags
    #########################################################################

    def set_flag(self, key, val):
        """
        assigns a value to the flag 'key'
        """
        self.flags[key] = val
        
    def get_flag(self, key, error_type = WARNING):
        """
        get the value stored in the flag 'key'
        """
        if not(key in self.flags.keys()):
            self.signal(error_type, "%s flag not initialized yet!!!"%key)
            return None
        return self.flags[key]
    
    #########################################################################
    # management of multidimensional arrays global arrays
    #########################################################################
    
    def process_key(self, tab, key, error_type=CRITICAL):
        """
        maps the key of a tab into a more manageable string
        """
        if not(tab in self.tabs.keys()):
            self.signal(error_type, "%s tab is still empty!!!" % tab)
            return None
        if type(key) == type([1, 2]):
            # multidimensional indexing of the array
            keymapped = JOIN_SEPARATOR1.join(key)
        else:
            keymapped = key
        return keymapped
        
    def set_tab_val(self, tab, key, val):
        """
        assigns a value into the tab 'tab' at the key 'key'
        """
        if not(tab in self.tabs.keys()):
            self.tabs[tab] = {}
        self.tabs[tab][self.process_key(tab, key)] = val
        
    def get_tab_val(self, tab, key, error_type = WARNING):
        """
        get the value stored in the tab for the key 'key'
        """
        if not(tab in self.tabs.keys()):
            self.signal(error_type, "%s tab is still empty!!!"%tab)
            return None
        keymapped = self.process_key(tab, key)
        if not(keymapped in self.tabs[tab].keys()):
            self.signal(error_type,
                        "%s value not initialized yet in %s tab!!!" %\
                        (keymapped, tab))
            return None
        return self.tabs[tab][keymapped]
        
    def get_tab_keys(self, tab, error_type = WARNING):
        """
        get the values stored in the tab for the key 'key'
        """        
        if not(tab in self.tabs.keys()):
            self.signal(error_type, "%s tab is still empty!!!"%tab)
            return []
        dim = self.get_tab_dim(tab, error_type)
        if dim == 1:
            # monodimensional array : getting immediatly the keys!
            return self.tabs[tab].keys()
        # multi-dimensional array --> building the key list in all dimension
        keys = {}
        for i in range(dim):
            keys[i] = {}
        
        for kesin in self.tabs[tab].keys():
            kys = str.split(kesin, JOIN_SEPARATOR1)
            i = 0
            for k in kys:
                keys[i][k] = 1
                i = i+1

        for i in range(dim):
            keys[i] = keys[i].keys()
            
        
        return keys

    def get_tab_list(self):
        """ returns list of tabs"""
        return self.tabs.keys()
    
    def get_tab_dim(self, tab, error_type = WARNING):
        """ return the dimension of a tab """
        if not(tab in self.tabs.keys()):
            self.signal(error_type, "%s tab is still empty!!!"%tab)
            return 0
        dim = 0
        for key in self.tabs[tab].keys():
            dim = max(len(key.split(JOIN_SEPARATOR1)), dim)
        return dim
        
MSG = MessageCenter()
MSG_PINGER = MessageCenter()


def save_env(tag_name):
    """ save Environnement variables (flags, balises...)"""
    MSG.save_env(tag_name)
    
def load_env(tag_name):
    """ restore Environnement variables (flags, balises...)"""
    MSG.load_env(tag_name)

def signal(signal_type, message, *args):
    """ send a signal """
    MSG.signal(signal_type, message, *args)

def send_message(stream, message, mode = "w"):
    """ send a message """
    #--debugging false logger message 
    # print "stream, message, mode : ",stream, message, modestream, message, mode
    MSG.send_message(stream, message, mode)
    
def stack_add(stack, message):
    """ add a message to the stack"""
    MSG.stack_add(stack, message)
    
def set_balises(*balise_and_values, **dico):
    """ set the values of several balises in one shot""" 
    if len(balise_and_values)%2:
        signal(CRITICAL, "not an equal number of balise and values!")
    for  i in range(len(balise_and_values)/2):
        MSG.set_balise(balise_and_values[i*2], balise_and_values[i*2+1])
    for balise in dico.keys():
        MSG.set_balise(balise, dico[balise])
    
def set_balise(balise, value):
    """ set a balise """
    MSG.set_balise(balise, value)
    
def get_balise(balise, error_type = WARNING):
    """ get the value of a balise """
    return MSG.get_balise(balise, error_type)

def get_balises():
    """ get the values of a balise """
    return MSG.balises
def set_flag(flag, value):
    """ set the value of a flag"""
    MSG.set_flag(flag, value)
    
def get_flag(flag, error_type = WARNING):
    """ set the value of a flag """
    return MSG.get_flag(flag, error_type)

def set_tab_val(tab, key, val):
    """ ????? """
    return MSG.set_tab_val(tab, key, val)
    
def get_tab_val(tab, key, error_type = WARNING):
    """ ????? """
    return MSG.get_tab_val(tab, key, error_type)

def get_tab_keys(tab, error_type = WARNING):
    """ ????? """
    return MSG.get_tab_keys(tab, error_type)

def get_tab_list():
    """ ????? """
    return MSG.get_tab_list()

def get_tab_dim(tab, error_type = WARNING):
    """ ????? """
    return MSG.get_tab_dim(tab, error_type)

