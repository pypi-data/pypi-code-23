
#!/opt/oss/bin/python

"""
module handling log messages
"""

import cPickle
import logging
import logging.handlers
import SocketServer
import struct
import os, sys, time, getopt, threading
import subprocess

from messages import send_message, MSG, get_flag, set_flag
from fichiers import grep
from env import MY_MACHINE_FULL_NAME, PYTHON_EXE
from launcher import MY_LAUNCHER, set_scheduler

HANDLED_LOGGERS = {}


HANDLED_LOGGERS = {}
MACHINE_NAME = ""
PORT = ""
DIRECTORY = ""

LOG_DIRECTORY = ""
ABORT = False
NB_JOBS = 0
NB_JOBS_DONE = 0
NB_JOBS_FAILED = 0
RUNNING_JOBS = {}
NOT_SCHEDULED = 0

TO_BE_INSTALLED =  {}
ALREADY_INSTALLED =  {}
NB_MESSAGES = {}

JOBNAME = "unknown"
TIME_LAST_PING = time.time()

set_flag("debug", 0)
set_flag("test_only", False)
set_flag("launch_sequential_jobs", False)

def parse():
    """
    parsing command line and initialize global variables
    """
    global MACHINE_NAME, PORT, DIRECTORY, NB_JOBS, \
           JOBNAME, LOG_DIRECTORY, MY_LAUNCHER
    try:
        opts,  args = getopt.getopt(sys.argv[1:],  "l",  
                    ["launch_logger=", "log_directory=", "launch_sequential_jobs",
                     "debug", "debuglogger", "project=", "checksum_id=", "timestamp="])
    except getopt.GetoptError,  err:
        # print help information and exit:
        print "ERROR while parsing request: ", err
        print "goodbye logger..."
        sys.exit(1)
    set_flag("debug", False)
    for option, argument in opts:
        if option in ("--launch_logger"):
            print argument
            logger_type,MACHINE_NAME, PORT, DIRECTORY, NB_JOBS = argument.split("::")
            PORT = int(PORT)
            NB_JOBS = int(NB_JOBS)
            MY_LAUNCHER = set_scheduler(logger_type)
            print "\t IMPORTANT for checking also queue scheduler type forced to the one of ",logger_type
            print "listening on %s:%d for %d jobs" % \
                (MACHINE_NAME, PORT, NB_JOBS)
        elif option in ("--debug"):
            set_flag("debug", True)
        elif option in ("--debuglogger"):
            set_flag("debug", True)
        elif option in ("--checksum_id"):
            set_flag("checksum_id", True)
        elif option in ("--launch_sequential_jobs"):
            set_flag("launch_sequential_jobs", True)
        elif option in ("--timestamp"):
            set_flag("timestamp", True)
        elif option in ("--project"):
            JOBNAME = argument
        elif option in ("--log_directory"):
            LOG_DIRECTORY = argument
            MSG.killing_filename = "%s/KILLED" % (argument)
            if not os.path.isdir(argument):
                os.makedirs(argument)
                print "creation,  dir ", argument
        else:
            assert False,  "unhandled option"
            print "goodbye logger..."
            sys.exit(1)


def ping_checking():
    """
    checks if a job is still running
    if not, kills the whole process
    """
    global ABORT,NOT_SCHEDULED, TIME_LAST_PING


    if (os.path.isfile(MSG.killing_filename)):
        print "KILLED : process killed by external order"
        ABORT = True 
        return

    time_since_last_pinged = time.time()-TIME_LAST_PING
    if get_flag("debug"):
        print "last pinging : %s seconds..."%(time_since_last_pinged)

    if (time_since_last_pinged < 125 and not ABORT):
        # ok something has pung in the last 2 minutes
        NOT_SCHEDULED=0
        threading.Timer(60.0, ping_checking).start()
        return


    job_exists = MY_LAUNCHER.stat(JOBNAME, verbose=False)

    if get_flag("debug"):
        print "last pinging : %s seconds... %s process still running" \
              % (time_since_last_pinged,job_exists)
            
    if (not(job_exists)) :
        NOT_SCHEDULED =  NOT_SCHEDULED +1
        print "STRANGE : No other process is running! for the %d th time!"% NOT_SCHEDULED
        if NOT_SCHEDULED==3:
            print "KILLED : No other process is running! 3 times and I'm out... \ngoodbye logger"
            ABORT = True
        else:
            TIME_LAST_PING = time.time()
            threading.Timer(60.0, ping_checking).start()
    else:
        TIME_LAST_PING = time.time()
        NOT_SCHEDULED = 0
        threading.Timer(60.0, ping_checking).start()




class LogRecordStreamHandler(SocketServer.StreamRequestHandler):
    """
    Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """


    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while 1:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack(">L", chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = cPickle.loads(chunk)
            record = logging.makeLogRecord(obj)
            self.handle_log_record(record)

    def handle_log_record(self, record):
        """
        handle a log line received from any of the workers.
        """
        # if a name is specified, we use the named logger rather than the one
        # implied by the record.


        if self.server.logname is not None:
            name = self.server.logname
        else:
            (mode, name) = str.split(record.name, ":-:")
            if get_flag('debug'):
                print mode, name
            mode = str.replace(mode, "G", "")
            if len(mode) == 0:
                mode = "a"

        if get_flag("debug"):
            what = record.getMessage()
            print "received message with what=",what,"name=",name
            print "server.logname=",self.server.logname

        if not name in HANDLED_LOGGERS.keys():
            logger = logging.getLogger('global_%s' % name)
            logger.propagate = 0
            logger.setLevel(logging.INFO)
            log_file_name = "%s/LOGS/" % LOG_DIRECTORY+name+".log"
            if get_flag('debug'):
                print "SSSSSSS getLogger(%s) SSSSSSSS  --> %s" \
                % (name, log_file_name)

            open(log_file_name, mode).close()

            handler = logging.handlers.RotatingFileHandler(
                 log_file_name, maxBytes = 20000000,  backupCount = 5)

            formatter = logging.Formatter("%(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            HANDLED_LOGGERS[name] = logger
        else:
            logger = HANDLED_LOGGERS[name]

        if str.find(name, "logger")>=0 or str.find(name, "status")>=0:
            # info to follow the run
            self.process_log_info(record, logger)
        else:
            logger.handle(record)



    def process_log_info(self, record, logger):
        """
        especially process log giving information on the
        execution covering of the jobs ongoing
        """
        global ABORT, NB_JOBS_DONE, NB_JOBS, NB_JOBS_FAILED, \
               RUNNING_JOBS, TIME_LAST_PING, LOG_DIRECTORY, \
               TO_BE_INSTALLED, CURRENT_INSTALLED 


        TIME_LAST_PING = time.time()
        time_str = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        what = record.getMessage()

        try:

            if get_flag("debug"):
                print "processing ....", what
                
            if str.find(what, "Exit") >= 0:
                logger.info('received Exit order %s' % time_str)
                logger.info('KILLED %s' % time_str)
                time.sleep(2)
                ABORT = True
                return

            if str.find(what,"Installation")>=0:
                (nb_job,message) = what.split(" : ")
                
                if str.find(what,"Checking")>=0:
                    TO_BE_INSTALLED[nb_job]=1
                    HANDLED_LOGGERS["logger"].info(
                        "%s jobs done ( %s failed ) out of %s  = %6.2f %% (%s running, %s installing) %s" % \
                    (NB_JOBS_DONE, NB_JOBS_FAILED, NB_JOBS, \
                         100.*NB_JOBS_DONE/NB_JOBS, \
                         len(RUNNING_JOBS), len(TO_BE_INSTALLED),\
                       time_str))
                    
                if str.find(what,"Ongoing")>=0:
                    TO_BE_INSTALLED[nb_job]=1
                    HANDLED_LOGGERS["logger"].info(
                        "%s jobs done ( %s failed ) out of %s  = %6.2f %% (%s running, %s installing) %s" % \
                    (NB_JOBS_DONE, NB_JOBS_FAILED, NB_JOBS, \
                         100.*NB_JOBS_DONE/NB_JOBS, \
                         len(RUNNING_JOBS), len(TO_BE_INSTALLED), \
                       time_str))

                if str.find(what,"OK")>=0:
                    (nb_job,message) = what.split(" : ")
                    ALREADY_INSTALLED[nb_job]=1
                    if nb_job in TO_BE_INSTALLED.keys():
                        del TO_BE_INSTALLED[nb_job]
                        HANDLED_LOGGERS["logger"].info(
                        "%s jobs done ( %s failed ) out of %s  = %6.2f %% (%s running, %s installing) %s" % \
                            (NB_JOBS_DONE, NB_JOBS_FAILED, NB_JOBS, \
                                 100.*NB_JOBS_DONE/NB_JOBS, \
                                 len(RUNNING_JOBS), len(TO_BE_INSTALLED), \
                                 time_str))

                logger.info(what)
                return

            if str.find(what, "Processing")>=0:
                (nb_job,message) = what.split(" : ")
                RUNNING_JOBS[nb_job] = time.time()
                HANDLED_LOGGERS["logger"].info(
                    "%s jobs done ( %s failed ) out of %s  = %6.2f %% (%s running, %s installing) %s" % \
                    (NB_JOBS_DONE, NB_JOBS_FAILED, NB_JOBS, \
                         100.*NB_JOBS_DONE/NB_JOBS, \
                         len(RUNNING_JOBS), len(TO_BE_INSTALLED),  \
                       time_str))
                return
                
            if str.find(what, "Terminated")>=0:
                (nb_job,message) = what.split(" : ")
                try:
                    del RUNNING_JOBS[nb_job]
                    if str.find(what, "CRITICAL")>=0:
                        NB_JOBS_FAILED = NB_JOBS_FAILED +1
                except:
                    if get_flag("debug"):
                        HANDLED_LOGGERS["logger"].info(
                            "!!!!! job #%s Terminated twice !!!!!! %s \n" % (nb_job,time_str))
                    NB_JOBS_DONE = NB_JOBS_DONE+1
                    HANDLED_LOGGERS["logger"].info(
                        "%s jobs done ( %s failed ) out of %s  = %6.2f %% (%s running, %s installing) %s" % \
                        (NB_JOBS_DONE, NB_JOBS_FAILED, NB_JOBS, \
                         100.*NB_JOBS_DONE/NB_JOBS, \
                         len(RUNNING_JOBS), len(TO_BE_INSTALLED),\
                       time_str))
                    if NB_JOBS_DONE == NB_JOBS:
                        HANDLED_LOGGERS["logger"].info("goodbye : all %s jobs done ( %s failed )  %s" % \
                                                       (NB_JOBS, NB_JOBS_FAILED, time_str))
                        logger.info(what)
                        HANDLED_LOGGERS["logger"].flush()
                        time.sleep(10)
                        ABORT = True
                        return
                    logger.handle(record)
                    
                    return

            if str.find(what, "Terminated")>=0:
                NB_JOBS_DONE = NB_JOBS_DONE+1
                HANDLED_LOGGERS["logger"].info(
                    "%s jobs done ( %s failed ) out of %s  = %6.2f %% (%s running, %s installing) %s" % \
                    (NB_JOBS_DONE, NB_JOBS_FAILED, NB_JOBS, \
                         100.*NB_JOBS_DONE/NB_JOBS, \
                         len(RUNNING_JOBS), len(TO_BE_INSTALLED),\
                       time_str))
                if NB_JOBS_DONE == NB_JOBS:
                    HANDLED_LOGGERS["logger"].info("goodbye : all %s jobs done ( %s failed )  %s" % \
                                (NB_JOBS, NB_JOBS_FAILED, time_str))
                    logger.info(what)
                    HANDLED_LOGGERS["logger"].flush()
                    time.sleep(10)
                    ABORT = True
                    return
                logger.handle(record)
                return

            if str.find(what, "Ping from")>=0:
                return
        
        
            # another message is received;..
            if get_flag("debug"):
                logger.info("!!!!! Pb another message received : /%s/",what)

        except:
            print "!!!!! Pb handling log : /%s/" % what
            HANDLED_LOGGERS["logger"].info(
                "!!!!! Pb handling log : /%s/" % what)
            

class LogRecordSocketReceiver(SocketServer.ThreadingTCPServer):
    """simple TCP socket-based logging receiver suitable for testing.
    """

    allow_reuse_address = 1

    def __init__(self, host,
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=LogRecordStreamHandler):
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.timeout = 1
        self.logname = None

    def serve_until_stopped(self):
        """
        endless loop that run a listening Logger
        """
        import select

        ping_checking()
        
        while not ABORT:
            #print "ABORT=", ABORT
            if not(ABORT):
                read, write,  exception = \
                    select.select([self.socket.fileno()], 
                                       [],  [], 
                                       self.timeout)
                if read and not ABORT:
                    self.handle_request()
                if write or exception:
                    print "write or exception not handled here"
        which2kill = " kill -9 %s " % os.getpid()
        if os.name == "nt":
            pass
        else:
            #os.system(which2kill)
            pass

def start_logger(machine_name, port):
    """
    test logger run
    """

    logging.basicConfig(format="%(message)s")
#    tcp_server = LogRecordSocketReceiver("rendvous-fn1")

    # getting first port available
    tcp_server = LogRecordSocketReceiver(machine_name, port)

    if get_flag('debug') or get_flag('test_only'):
        print "About to start TCP server... on port %d" % port

    tcp_server.serve_until_stopped()
    #tcp_server.serve_forever()


###############################################################
# lauching logger
###############################################################


def search_available_logging_port(host_name=MY_MACHINE_FULL_NAME):
    """
    scans available ports and returns the first one free
    that can used by the logger
    """
    logging.basicConfig(
        format = "%(send_message)s")
    #
    # searching a free port
    #
    port = logging.handlers.DEFAULT_TCP_LOGGING_PORT+12
    not_ok = True
    while not_ok:
        try:
            LogRecordSocketReceiver(host_name, port)
            not_ok = False
        except:
            port = port+1

    if False and get_flag("debug"):
        send_message("maestro",
                     "About to start TCP server... for host %s on port %d" % \
                     (host_name, port),"G")
    return host_name, port



def launch_server(host_name, port):
    """ launch logserver on host and port given """
    logging.basicConfig(format="%(send_message)s")
    tcpserver = LogRecordSocketReceiver(host_name, port)
    if not get_flag("test_only"):
        send_message("std", 
                     "starting TCP server... for host %s on port %d"\
                     %(host_name, port))
        send_message("std", 
                     "starting TCP server... for host %s on port %d"\
                     %(host_name, port))
        tcpserver.serve_until_stopped()
    else:
        send_message("std", 
                     "should start TCP server... for host %s on port %d" \
                     %(host_name, port))

def spawn_logger(logger_type, log_directory, jobname, checksum_id, timestamp):
    """ global process starting the logger """
    # 2.1) search for available port
    machine_name, port = search_available_logging_port()
    set_flag("logServerPort", port)
    set_flag("logServerName", machine_name)
    # 2.2)
    if get_flag("debug"):
        out_stream =  "> %s/LOGS/logger_debug_output.log 2> %s/LOGS/logger_debug_error.log" % \
                     (get_flag("results_directory"),get_flag("results_directory"))
        debug_flag = "--debug"
    else:
        out_stream = "> /dev/null 2> /dev/null "
        debug_flag = ""
    MAESTRO_PATH = os.getenv("MAESTRO_PATH")
    if not(MAESTRO_PATH):
        MAESTRO_PATH = "/opt/slurm/etc/maestro/1.5"
        print "\n\t!!! MAESTRO_PATH forced at ",MAESTRO_PATH
    command = ("-u %s/maestro/logserver.py "\
             +"--checksum_id=%s --timestamp=%s "
             +"--launch_logger=%s::%s::%s::%s::-1 "\
             +"--log_directory=%s/%s --project=%s %s ") % \
             (MAESTRO_PATH,checksum_id, timestamp,
              logger_type, machine_name,  port,  MSG.maestro_directory, \
              MSG.maestro_directory,log_directory, jobname, debug_flag)
    if get_flag("launch_sequential_jobs"):
        command = command + "--launch_sequential_jobs"
        command = command + out_stream + "&"
        
    if get_flag("test_only"):
        print "should be launching \n\t%s" % command
    else:
        send_message("std", "\n\tstarting logger...")
        if get_flag('debug'):
            send_message("std", 
                     "\tspawning logger in dir=%s/%s listening to %s:%s" % \
                     (MSG.maestro_directory, log_directory, machine_name, port))
            send_message("std", "launching \n\t%s"%command)
        #print command
        #os.system(PYTHON_EXE+" "+command)
        spawn_process(PYTHON_EXE, command)
        if get_flag('debug'):
            print "\n\tspawning logger"
        
    print "\n\twaiting for logger to start"
    if not(get_flag("test_only")):
        time.sleep(6)
        #send_message("deploy", "launching logger...\n\t%s" % command, "G")


    return machine_name, port


def spawn_process(program, *args):
    """
    spawning process... works under windows also
    returns tid of the process 
    """
    if os.name == "nt": 
        spawn = os.spawnv
        return spawn(os.P_NOWAIT, program, (program,) + args)
    else:   
        #spawn = os.spawnvp #not available on windows
        #return spawn(os.P_NOWAIT, program, (program,) + args)
        program = "nohup "+program+" "+" ".join(args)
        if not get_flag("launch_sequential_jobs"):
            # if submited via MPI or parallel python, logging process can be put in background because
            # it won't be killed
            program = program + "&"
        else:
            # in the case of sequential submission logging process has to be hold and kept running
            # in foreground otherwise it's killed by the scheduler
            pass
        if get_flag('debug'):
            print "process spawned : ",program
        return os.system(program)
        #print "program : %s " % (program+" ".join(args))
        #pid = subprocess.Popen([program, " ". join(args)]).pid
        #return pid


def get_nb_job_total():
    global NB_JOBS, LOG_DIRECTORY

    jobs_filename="%s/LOGS/Jobs.log" % LOG_DIRECTORY
    NB_JOBS=int(grep("Job_total",jobs_filename,1))
    print NB_JOBS


def create_logfile():
    name="logger"
    logger = logging.getLogger('global_%s' % name)
    logger.propagate = 0
    logger.setLevel(logging.INFO)
    log_file_name = "%s/LOGS/" % LOG_DIRECTORY+name+".log"
    if get_flag('debug'):
        print "SSSSSSS getLogger(%s) SSSSSSSS  --> %s" \
        % (name, log_file_name)

    logfile=open(log_file_name, "a").close()

    handler = logging.handlers.RotatingFileHandler(
         log_file_name, maxBytes = 20000000,  backupCount = 5)

    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    HANDLED_LOGGERS[name] = logger

    time_str = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    logger.info("STARTING  PROCESS = %s jobs todo %s"  % \
                        (NB_JOBS, time_str))

if __name__ == "__main__":
    parse()
    get_nb_job_total()
    create_logfile()
    start_logger(MACHINE_NAME, PORT)
