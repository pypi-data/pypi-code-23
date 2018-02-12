#-*-coding:iso-8859-1-*-
#!/logiciels/public/bin/python-2.4
"""
module managing launch, monitor, halt of the process
"""
import getopt, sys, os
import threading, shutil, glob, time
import exceptions, traceback
import math

from fichiers  import grep, greps, get_checksum_id, get_timestamp
from messages  import \
     signal, set_flag, get_flag, \
     MSG, MSG_PINGER, \
     CRITICAL, ERROR, send_message, \
     get_tab_val, set_tab_val, Timer, \
     load_env, save_env, \
     get_tab_list, get_tab_keys, get_tab_dim, \
     MyError, MyErrorNoExit, GV
from avanti    import Avanti
from launcher import MY_LAUNCHER
from env       import MY_MACHINE, MY_MACHINE_FULL_NAME, TMPDIR, CORE_PER_NODE_REGARDING_QUEUE, DEFAULT_QUEUE
from logserver import spawn_logger, launch_server
from info import get_info, get_bilan


#############################################################################
# classe job
#   - moteur principal de calcul
#   - sauvegarde des resultats
#############################################################################
#

COUNT = 1
RUN = 2
DEPLOY = 3

set_flag("my_job", -1)
set_flag("debug", 0)
set_flag("debuglogger", 0)
set_flag("debugjobs", 0)
set_flag("debugoutput", 0)
set_flag("nocleaning", False)
set_flag("test_only", False)
set_flag("pinging", True)
set_flag("uncheck", False)
set_flag("no_stop_on_break", False)
set_flag("test_only", False)
set_flag("status", False)
set_flag("reservation", False)
set_flag("machines", False)
set_flag("tasks-per-job", 1)
set_flag("tasks", 1)
set_flag("gather", False)
set_flag("resume", False)
set_flag("depth",888)
set_flag("wall-time-1-job", "00:10:00")
set_flag("wall-time-avanti-job", "24:00:00")
set_flag("spawn_logger",False)
set_flag("result","")
set_flag("make_jobs_list",False)
set_flag("jobs_list",False)
set_flag("sequential_job",False)
set_flag("launch_sequential_jobs",False)
set_flag("time_flag", False)
set_flag("account", False)
set_flag("ppn",False)
set_flag("server","0")
set_flag("queue",DEFAULT_QUEUE)

set_flag('initial_dir',os.getcwd())

def welcome_message():
    """ welcome message"""
    
    print """
                   #########################################
                   #                                       #
                   #   Welcome to MAESTRO Framework 1.6!   #
                   #                                       #
                   #########################################

                   
     """
    print "\n\trunning on %s (%s) " %(MY_MACHINE_FULL_NAME,MY_MACHINE)
    print "\n\tprocessing ..."
    print "\t\t", " ".join(sys.argv)


def usage(message = None,exiting = True):
    """ helping message"""
    if message:
        print message
    print "  usage: \n \t python module.py \
             \n\t\t[ --help ]\
             \n\t\t--cores=<nb_cores> [--account=<account>] \
             \n\t\t[\t[ --tasks-per-job=<nb_tasks_per_job_to_run_in_parallel>]\
             \n\t\t[\t[ --queue=<specific queue to run the jobs on> ]\
             \n\t\t\t[ --time=hh:mm:ss ] [ --depth=<in depth parallelism>    ] ] \
             \n\t\t[ --kill | --restart | --stat] "
    if exiting :
        print
        sys.exit(1)

def advanced_usage(message = None):
    """ helping message with all hidden option """
    if message:
        print message
    usage(exiting = False)
    print "   \n\t\t[ --reservation=<reservation_id> ]\
             \n\t\t[ --debug ] [ --debuglogger ] [ --debugjobs ] [ --debugoutput ] [--nocleaning] \
             \n\t\t[ --kill | --restart | --resume ] \
             \n\t\t[ --make_jobs_list ] \
             \n\t\t[ --exec_job=<job number to execute> --jobs_list=<job list file> ] \
             \n\t\t[ --ppn=<nb_process_per_node> ] \
             \n\t\t[ --tasks-per-job=<nb_tasks_per_elementary_run> ] \
             \n\t\t[ --result=<result_dir> ] \
             \n\t\t[ --stat | --bilan | --info=<job_id> ] \
             \n\t\t[ --machines=<machines_file_name> ] \
             \n\t\t[ --logto=<machine name> ]\
             \n\t\t[ --uncheck | --clean | --restart | --kill ] \
             \n\t\t[ --test | --debug | --list_process ] \
             \n\t\t[ --gather ] "

    sys.exit(1)


#############################################################################
#
#############################################################################

class Job:

    """
    main class orchestrating the scheduling of jobs *
    """

    def __init__(self, description, results_dir, calcul):



        self.results_directory = results_dir
        self.results_directory_relative_path = results_dir

        MSG.results_directory = "%s/%s/" % \
                            (MSG.maestro_directory, self.results_directory)
        set_flag("results_directory", MSG.results_directory)
        MSG.killing_filename = "%s/LOGS/KILLED" % (MSG.results_directory)

        # calculating the unique identifier
        global_path = "%s+%s"%(os.getcwd(),results_dir)
        self.checksum_id = get_checksum_id(description,global_path)
        if get_flag("debug"):
            print "\tcalcul du checksum_id avec global_path=///%s/// et checksum_id=%s" % (global_path,checksum_id)
        set_flag("checksum_id", self.checksum_id)
        self.timestamp   = get_timestamp()
        set_flag('timestamp',self.timestamp)
        
        self.description = description
        set_flag("job_description", description)
        self.jobname = str.replace("%s_%s" % \
                                   (self.checksum_id,self.description), \
                                   " ", "_")
        self.jobname = self.jobname[:16]
 
        self.vars = []
        self.nb_vars = 0
        self.sets = {}
        self.set_dim = {}
        self.calculate_index = {}

        self.calcul =  None

        self.etape = {}
        self.etat = {}
        self.etat_final = {}
        self.result = {}
        self.traces = {}
        self._flags = {}

        self.indices = None

        self.nb_job = 0
        self.my_job = -1
        self.depth = -1
        self.nb_jobs = 0
        
        self.job_indices = {}
        self.initial_indices = []

        self.deploy_on_cluster_first = False
        self.nb_procs = None
        self.account = None

        self.starting_path = os.getcwd()

        MSG.stack_add("stack", description)

        self.calcul = calcul
        self.calcul.job = self
        MSG.stack_add("stack", str(calcul.__class__).replace("__main__.",  ""))


        self.logger_machine_name = ""
        self.nb_job_total = -1
        self.logger_port = 0
        self.temps_calcul = 0
        self.contexte = ""
        self.values = ""
        self.count_print=False

        self.parse()
        
        self.init_calculation()


    def ping_logger(self):
        """ regularly pings the logger so that it knows job is running"""

        global MSG_PINGER
        
        self.shall_stop()
        MSG_PINGER.send_message("logger", "Ping from %d"%get_flag("my_job"), "G")
        if get_flag("debug"):
            print "pinging", get_flag("pinging")        
        if get_flag("pinging"):            
            threading.Timer(10.0,  self.ping_logger).start()
        else:
            if get_flag("debug"):
                print "ok finishes pingging logger"

    def kill_logger(self):
        """ kill the logger remotely """
        send_message("logger", "Exit", "G")



    #########################################################################
    # command line parsing...
    #########################################################################

    def parse(self):
        """ parse the command line and set global _flags according to it """
        set_flag("progname", sys.argv[0])
        try:
            opts, args = getopt.getopt(sys.argv[1:], "Hht", 
                              ["help", "HELP","make_jobs_list", "jobs_list=", "job=",
                               "exec_job=", "checksum_id=", "timestamp=", 
                               "depth=", "procs=", "cores=", "account=", "reservation=", "time=",
                               "clean", "kill", "uncheck",
                               "restart", "resume", "status", "bilan", "info=", 
                               "result=","ppn=","tasks-per-job=","queue=","server=",
                               "xxx=", "logto=", "gather",
                               "test", "indices=", "debug", "debuglogger", "debugjobs", "debugoutput", "nocleaning",
                               "list_process", "project=",
                               "spawn_logger=", "launch_logger=",  "log_directory=", "launch_sequential_jobs"])
        except getopt.GetoptError, err:
            # print help information and exit:
            usage(err)
            signal(CRITICAL,"err")

        # first scan opf option to get prioritary one first
        # those who sets the state of the process
        # especially those only setting flags are expected here
        for option, argument in opts:
            if option in ("-h", "--help"):
                usage("")
            elif option in ("-H", "--HELP"):
                advanced_usage("")
            elif option in ("--debug"):
                set_flag("debug", 1)
            elif option in ("--debuglogger"):
                set_flag("debuglogger", 1)
            elif option in ("--debugjobs"):
                set_flag("debugjobs", 1)
            elif option in ("--debugoutput"):
                set_flag("debugoutput", 1)
            elif option in ("--nocleaning"):
                set_flag("nocleaning", 1)
            elif option in ("--gather"):
                set_flag("gather", 1)
            elif option in ("--launch_sequential_jobs"):
                set_flag("launch_sequential_jobs", True)
            elif option in ("--time"):
                set_flag("wall-time-1-job", argument)
                set_flag("wall-time-avanti-job", argument)
                set_flag("time_flag",True)
            elif option in ("--test","-t"):
                set_flag("test_only", True)
                set_flag("uncheck", True)
            elif option in ("--uncheck"):
                set_flag("uncheck", True)
            elif option in ("--make_jobs_list"):
                set_flag("make_jobs_list", True)
            elif option in ("--jobs_list"):
                self.jobs_list = argument
                set_flag("jobs_list", argument)
            elif option in ("--checksum_id"):
                self.checksum_id = argument
                set_flag("checksum_id", argument)
            elif option in ("--timestamp"):
                self.timestamp = argument
                set_flag("timestamp", argument)
            elif option in ("--reservation"):
                set_flag("reservation", argument)
            elif option in ("-j", "--job"):
                self.my_job = int(argument)
                set_flag("my_job", int(argument))
            elif option in ("--indices"):
                set_flag("indices", argument)
            elif option in ("--indices"):
                set_flag("indices", argument)
            elif option in ("--project"):
                pass
            elif option in ("--ppn"):
                set_flag("ppn",argument)
            elif option in ("--tasks-per-job"):
                set_flag("tasks-per-job",argument)
                set_flag("tasks",argument)
            elif option in ("--queue"):
                set_flag("queue",argument)
                if argument in CORE_PER_NODE_REGARDING_QUEUE.keys():
                    set_flag("ppn",CORE_PER_NODE_REGARDING_QUEUE[argument])
            elif option in ("--server"):
                if len(argument):
                    set_flag("server",argument)
            elif option in ("--result"):
                set_flag("result", "--result=%s"%argument)
                self.results_directory = argument
                self.results_directory_relative_path = argument
                MSG.results_directory = "%s/%s/" % \
                    (MSG.maestro_directory, self.results_directory)
                set_flag("results_directory", MSG.results_directory)
                MSG.killing_filename = "%s/LOGS/KILLED" % (MSG.results_directory)
            elif option in ("--log_directory"):
                set_flag("log_directory", argument)
                # replacing the right directory in case
                # of a copy of the script is run
                MSG.maestro_directory = "%s/../"%argument
                MSG.results_directory = "%s/%s/" % \
                            (MSG.maestro_directory, self.results_directory)
                set_flag("results_directory", MSG.results_directory)
                MSG.killing_filename = "%s/LOGS/KILLED" % (MSG.results_directory)
            elif option in ("--output_file"):
                set_flag("output_file", argument)
            elif option in ("--error_file"):
                set_flag("error_file", argument)
            elif option in ("--account"):
                self.account = argument
                set_flag("account", self.account)
            # more complex option, but no call to method are made yet
            
            elif option in ("--depth"):
                self.depth = int(argument)
                set_flag("depth",self.depth)
                all_args = " ".join(sys.argv[1:])
                if str.find(all_args,"--depth=") == -1:
                    usage("unknown option %s" % all_args)

            elif option in ("--logto"):
                self.logger_machine_name, self.logger_port = \
                                          argument.split("::")
                if get_flag("debug"):    
                    print "\t[DEBUG] self.logger_port = ",self.logger_port
                if self.logger_port == "UNKNOWN" or self.logger_port == "src" or self.logger_port[-1] == "3" :
                    # logger was not launched at the time this job was submitted
                    # we'll have to gather it
                    notYet = True
                    nbAttempt=10
                    while notYet and nbAttempt>0:
                        try:
                            if get_flag("debug") or get_flag("debuglogger"):    
                                os.system("ls -l %s/LOGS/logger_spawner_output.log " % (MSG.results_directory))
                                os.system("tail -3 %s/LOGS/logger_spawner_output.log " % (MSG.results_directory))
                            self.logger_machine_name, self.logger_port = \
                                                      grep("LOGGER_ADDRESS","%s/LOGS/logger_spawner_output.log" % (MSG.results_directory), [0,1])
                            print "\tLogger detected at %s:%s" % (self.logger_machine_name, self.logger_port)
                            notYet=False
                        except:
                            if get_flag("debug"):    
                                print "\tdetection of the port of the logger... attempt # %d failed " % int(11-nbAttempt)
                            nbAttempt = nbAttempt-1
                            time.sleep(20)
                    if notYet:
                        print "ERROR : could not find a logger alive"
                        sys.exit(0)
                self.logger_port = int(self.logger_port)
                set_flag("logger_name", self.logger_machine_name)
                set_flag("logger_port", self.logger_port)
            elif  option in ("--indices"):
                self.process_indices(argument)

        for option, argument in opts:            
            if option in ("-p", "--procs","--cores"):
                if option=="--procs":
                    print """
                ----------> <      WARNING     > <--------------
                the option --procs is now obsolete... and will
                    disapear in the next release of maestro!!!

                please use --cores instead (with the same meaning)

                Please modify your command
                ---------->  RESUMING CALCULATION  <-------------

                 """

                self.nb_procs = int(argument)
                self.deploy_on_cluster_first = True
                set_flag("my_job", 0)
                self.my_job = 0
                all_args = " ".join(sys.argv[1:])
                if str.find(all_args,"--procs=") == -1 and str.find(all_args,"--cores=") == -1:
                    usage("unknown option %s" % all_args)
                if self.nb_procs==0:
                    set_flag("sequential_job",True)
                    self.nb_procs = 4
                    if MY_MACHINE=="localhost" :
                        print """
                ----------> <      WARNING     > <--------------
                the option --cores=0 immediatly submit one job 
                    per elementary calculation and can only be 
                    used on an actual cluster!

                On this local machine, you can either 
                   - run your calculation sequentially, one 
                     elementary calculation after another :
                     using no --cores option at all
                   - run your calculation on a given number of
                     processes with the --cores=n  option 
                     where n>O.

                Please modify your command
                ---------->  END OF CALCULATION  <-------------
                 """
                        sys.exit(0)
                else:
                    if ((MY_MACHINE[:5]=="neser" or MY_MACHINE=="stampede") and not(self.account)):
                        print """
                ----------> <      WARNING     > <--------------
                the option --cores=n requires an information about 
                    the costing account on this machine.

                please add the parameter --account=kxx to your command

                Please modify your command
                ---------->  END OF CALCULATION  <-------------
                 """
                        sys.exit(0)

        # third scan of options to get those prioritary that neds to be run
        # first
        for option, argument in opts:
            if option in ("--kill"):
                self.kill_all(verbose=True)
                sys.exit(0)
            elif option in ("--restart"):
                self.restart_all()
                set_flag("uncheck", True)
            elif option in ("--resume"):
                self.kill_all(killing_myself=False,killing_logger=False)
                set_flag("resume", True)
                set_flag("uncheck", True)
            elif option in ("--clean"):
                self.kill_all()
                self.delete_all()
                sys.exit(0)
            elif option in ("--spawn_logger"):
                # gathering the type of logger to launch that will check also for job in queues
                # in the case of sequential jobs
                logger_type=argument
                #  spawning logger
                print "\n\tspawning logger..."
                if get_flag("debuglogger"):    
                    print "\t[DEBUG]... for machine=%s" % argument
                jobname = str.replace("%s_%s" % \
                                          (self.checksum_id,self.description), \
                                          " ", "_")
                jobname = jobname[:16]
                self.logger_machine_name, self.logger_port = \
                                          spawn_logger(logger_type,
                                                       self.results_directory,
                                                       jobname,
                                                       self.checksum_id, self.timestamp)
                set_flag("logger_name", self.logger_machine_name)
                set_flag("logger_port", self.logger_port)
                print self.logger_machine_name,self.logger_port,"       = LOGGER_ADDRESS"
                # waiting for the end of the logger
                filename_logger = "%s/LOGS/logger.log" % MSG.results_directory
                filename_logger_debug = "%s/LOGS/logger_debug_output.log" % MSG.results_directory
                while True:
                    if grep("goodbye",filename_logger) or grep("goodbye",filename_logger_debug):
                        print "goodbye catched"
                        time.sleep(60)
                        sys.exit(0)
                    time.sleep(10)
                    
                sys.exit(0)

        # third and final scan of options to get those left
        for option, argument in opts:
            if option in ("--exec_job"):
                # copying Jobs.log on tmp directory
                what = str.replace(self.description, " ", "_")
                if not(get_flag("jobs_list")):
                    jobs_list_org_file = "%s/LOGS/Jobs.log" % get_flag("log_directory")
                else:
                    jobs_list_org_file = get_flag("jobs_list")
                if get_flag("debug"):    
                    print "Fichier listant les jobs : ", jobs_list_org_file
                
                self.my_job = int(argument)

                # start pinging logger...
                if get_flag("logger_name"):
                    self.ping_logger()
                else:
                    if get_flag("debug"):
                        print "No logger defined for this run"
                        print send_message

                # checking if a restared job having that number exists
                restarted = grep("Restart_%d" % int(self.my_job),jobs_list_org_file, [1])

                if restarted:
                    # if it is restarted get the absolute number of the job
                    self.my_job = int(restarted)
                
                set_flag("my_job", int(argument))

                # reading indices from file
                ind = grep("Job_%d" % self.my_job, jobs_list_org_file, [1])
                self.process_indices(ind)                                
            elif option in ("--status"):
                set_flag("no_stop_on_break", True)
                set_flag("status", True)
                self.get_status(keep_probing=True)
                sys.exit(0)
            elif option in ("--bilan"):
                set_flag("no_stop_on_break", True)
                set_flag("status", True)
                get_bilan(keep_probing=True)
                self.kill_myself()
                sys.exit(0)
            elif option in ("--info"):
                job = int(argument)
                set_flag("no_stop_on_break", True)
                set_flag("status", True)
                #self.get_info(job, keep_probing=True)
                get_info(job)
                sys.exit(0)               
            elif option in ("--list_process"):
                set_flag("no_stop_on_break", True)
                set_flag("status", True)
                self.get_status(keep_probing=False, list_process=True)
                sys.exit(0)
            elif option in ("--launch_logger"):
                self.logger_machine_name, port, directory, nb_jobs \
                                          =  argument.split("::")
                self.logger_port = int(port)
                launch_server(self.logger_machine_name, self.logger_port)
                set_flag("logger_dir", directory)
                set_flag("nb_jobs_expected", int(nb_jobs))
                sys.exit(0)
            elif option in ("--xxx", "-h", "--help", "--debug", 
                            "--debuglogger", "--debugjobs", "--debugoutput", "--nocleaning", 
                            "--depth", "--gather", "--make_jobs_list", "--jobs_list", 
                            "--time", "--test", "-t",
                            "--uncheck", "--checksum_id", "--timestamp", 
                            "--reservation", "--logto",
                            "-j", "--job", "--indices", "--log_directory", "--project", 
                            "--procs", "--cores", "--account","--ppn","--tasks-per-job","--server","--queue",
                            "-clean", "--kill", "--clean", "--restart", "--resume", "--result",
                            "--output_file", "--error_file"):
                pass
            else:
                signal(CRITICAL, "unhandled option %s" % option)



    #########################################################################
    # managing Result directories...
    #########################################################################

    def init_calculation(self):
        """ create and initialize calculation environment"""
        # 1) creating results dir
        if self.my_job <= 0:
            # we are on the frontend node
            self.create_results_directory()

            # saving current script
            self.save_current_scripts()
            
            # saving my_pid into process.log file
            set_flag("my_pid", os.getpid())

        # installation of the environnement
        self.calcul.prepare()
        # todo : preparing a better deployement
        # self.calcul.prepare(get_flag("machines"))

        

    def create_results_directory(self):
        """create result directory where obtained results are stored"""
        if os.path.isdir(MSG.results_directory):
            if get_flag("status"):
                return
            if not get_flag("uncheck"):
                print """
                ----------> <      WARNING     > <--------------
                Result Dir '%s' 
                    already exists... created by another process 
                    that may be still running

                either change targetted Result Dir or erase the
                   already created one to run a new calculation.

                for the previous calculation you can use the 
                   following options : 
                   --kill    to kill the ongoing calculation 
                             and keep previous results   
                   --status  to obtain a detailed status on 
                             ongoing calculation
                   --restart to erase previous result, kill 
                            an eventual ongoing calculation
                             and start a new one

                Please modify your command
                ---------->  END OF CALCULATION  <-------------
                """ % MSG.results_directory

                sys.exit(0)
        else:
            try:
                os.makedirs(MSG.results_directory)
                os.makedirs(MSG.results_directory+"/RESULTS")
                os.makedirs(MSG.results_directory+"/LOGS")
                open(MSG.results_directory+"/LOGS/job.err", "w").close()
                open(MSG.results_directory+"/LOGS/job.out", "w").close()
            except:
                signal(CRITICAL,
                       "Result Dir '%s' could not be created!" \
                       % MSG.results_directory)
        if os.path.isfile(MSG.killing_filename):
            os.remove(MSG.killing_filename)


    def save_current_scripts(self):
        print "\n\tSaving scripts..."
        code_dir = "%s/BUNDLE/" % MSG.results_directory
        if os.path.isdir(code_dir):
                shutil.rmtree(code_dir)
        os.system('mkdir -p %s/dist; find -L . -not \( -wholename \*\/data/\* \) -not \( -wholename \*\/RESULTS/\* \)  -not \( -wholename \*\/BUNDLE\/\* \) \( -name \*.py -o -name \*.sh -o -name \*.dat \) | xargs tar rvf %s/dist/es.tar > %s/%s/BUNDLE/Code_files.out 2>&1'
                  % (code_dir,code_dir,MSG.maestro_directory,self.results_directory_relative_path))
        os.system("(cd %s/dist; tar xvf es.tar; rm es.tar; cd ..; mv dist Code; tar cfvz Code.tgz Code ) >>  %s/%s/BUNDLE/Code_files.out 2>&1" \
                  % (code_dir,MSG.maestro_directory,self.results_directory_relative_path))

    def get_status(self, keep_probing=False, list_process=False):
        """
        returns the status and the coverage of an ongoing or
        passed study
        """
        try:
            # attente de 200 s si plus de job
            no_process_running_checked_times = 200
            nb_process = MY_LAUNCHER.stat(self.jobname, list_process)

            filename = "%s/LOGS/logger.log" % MSG.results_directory

            good_bye_reached = False
            no_result_yet = True
            while no_result_yet:
                try:
                    line_good_bye=grep("goodbye",filename)
                    if grep("goodbye",filename):
                        good_bye_reached = True
                    no_result_yet = False
                except:
                    if os.path.isfile(MSG.killing_filename):
                        print "Job has been killed"
                        set_flag("pinging", False)
                        sys.exit(0)
                    print "Job hasn't started yet"
                    if not(keep_probing):
                        return
                sys.stdout.flush()

            if good_bye_reached:
                print
                print line_good_bye

                print "Job has reached its end"
                if keep_probing:
                    sys.exit(1)
                else:
                    return
                
        
            # tail log file
            if not os.path.isfile(filename):
                print "\n\tCannot get status yet : no logger is running...\n"
                signal(CRITICAL,"no logger yet")
                
            fic = open(filename, "r")
            lines = fic.readlines()
            print "\n","".join(lines[-2:])
            if str.find(lines[-1], "goodbye") >=0:
                good_bye_reached = True
            while True:
                where = fic.tell()
                line = fic.readline()
                nb_process = MY_LAUNCHER.stat(self.jobname, verbose=False)
                status = MY_LAUNCHER.get_status(self.jobname)
                if get_flag("debug"):
                    print nb_process, status
                if os.path.isfile(MSG.killing_filename):
                    print "Job has been killed"
                    set_flag("pinging", False)
                    sys.exit(0)
                if status == 'Q':
                    print "Job is queued but hasn't started yet"
                    time.sleep(10)
                if nb_process == 0:
                    no_process_running_checked_times = no_process_running_checked_times -1
                    if no_process_running_checked_times==0 :
                        break
                if not line:
                    time.sleep(10)
                    fic.seek(where)
                else:
                    print line, # already has newline
                    sys.stdout.flush()
                    if str.find(line,"goodbye") >= 0:
                        break
                if not(keep_probing):
                    break
                
            fic.close()

            if nb_process == 0:
                print "No process running anymore!!!"
                set_flag("pinging", False)
                sys.exit(0)
        except KeyboardInterrupt:
            print "\n bye bye come back anytime!"
            self.kill_myself()
        
    def restart_all(self):
        """
        restarting all 
        """

        if not(os.path.isdir(MSG.results_directory+"/LOGS")):
            # result directory does not exists anyway!
            os.makedirs(MSG.results_directory+"/LOGS")

        open(MSG.killing_filename, "w").close()
        MY_LAUNCHER.kill(self.jobname)
        time.sleep(1)

        os.remove(MSG.killing_filename)
        
        self.delete_all()


    def resume_all(self):
        """
        resuming all 
        """

        print "\n\tResuming calculation..."
        print "\t\tRetrieving information about previous run..."
        
        # getting number of jobs failed
        logger_filename = "%s/LOGS/logger.log" % MSG.results_directory
        starting_date, starting_time = \
                       grep("STARTING PROCESS",logger_filename, [6,7])
        print "\t\t\tLast run started at %s %s  " %\
              (starting_date, starting_time)

        try:
            nb_job_done,nb_job_failed, ending_date, ending_time = \
                       grep("goodbye",logger_filename,[3, 7, 10, 11])
            print "\t\t\t           ended at %s %s " %\
              (ending_date, ending_time)
        except:
            print "\t\t\tand never  ended..."
            logs = file(logger_filename,"r").readlines()
            nb_job_failed = 0
            for l in logs[-2:]:
                print l
                if str.find(l,"failed"):
                    fields = l.split(" ")
                    nb_job_failed = fields[4]
                    nb_job_done   = fields[0]

        nb_job_done   = int(nb_job_done)
        nb_job_failed = int(nb_job_failed)


        # getting total number of jobs
        print "\t\t\tTotal number of jobs todo \t: %s \t (%6.2f %%)" % \
              (self.nb_jobs,100)
        print "\t\t\tTotal number of jobs done \t: %s \t (%6.2f %%) " % \
              (nb_job_done,100*nb_job_done/self.nb_job_total)
        print "\t\t\tTotal number of jobs failed `\t: %s \t (%6.2f %%)" % \
              (nb_job_failed,100*nb_job_failed/self.nb_job_total)

        # getting critical jobs
        status_filename = "%s/status.log" % MSG.results_directory
        critical_jobs = greps("CRITICAL", status_filename, [0, 9, 7])
        print critical_jobs

        # erasing old result directory
        i=1
        for critical_job in critical_jobs:
            nb,ind,res = critical_job
            send_message("Jobs","Restart_%d %d"%(int(i),int(nb)),"w")
            i=i+1
            if os.path.isdir(res):
                shutil.rmtree(res)
            pass
        send_message("Jobs","Restart_total %d" % len(critical_jobs), "w")

        # recalculating job to do
        self.nb_jobs       = len(critical_jobs)
        self.nb_job_total  = len(critical_jobs)

        # erasing log and status file
        os.remove(status_filename)

        set_flag('resume',False)


    def kill_all(self ,verbose=False, killing_myself=True,
                 killing_logger=True):
        """
        killing all running process
        """

        if not(os.path.isdir(MSG.results_directory)):
            # result directory does not exists anyway!
            return
        
        fic = open(MSG.killing_filename, "w")
        fic.close()

        if verbose:
            send_message("std",
                         "=== killing log server === ")
        #self.get_status(keep_probing=False)
        # killing logger is made through the file killing_filename
        # at this point we may not even know the port of the logger (case of --kill)
        
        #if killing_logger:
        #    self.kill_logger()
        #    time.sleep(1)

        if verbose:
            send_message("std",
                         "=== killing Previous Study ongoing jobs === ")


        
        MY_LAUNCHER.kill(self.jobname)

        time.sleep(1)

        
        if verbose:
            send_message("std",
                         "=== Previous Study ongoing jobs Killed === ")
        #self.get_status(keep_probing=True)

        if killing_myself:
            self.kill_myself()


    def kill_myself(self):
        """ killing myself"""
        if os.name == "nt":
            kill_order="TASKKILL /PID %s /F" % os.getpid()
        else:
            kill_order = "kill -9 %s >/dev/null 2>&1" % os.getpid()
        if get_flag("debug"):
            print kill_order
        os.system(kill_order)
        

    def shall_stop(self):
        """ check if process should stop"""
        if os.path.isfile(MSG.killing_filename):
            send_message("logger", "suiciding %d"%get_flag("my_job"), "G)")
            print "Just received a Kill order : I am stopping..."
            self.kill_logger()
            self.kill_myself()
            sys.exit(1)
        return 0

    def delete_all(self):
        """ cleaning result of the previous study"""
        print "\n\tcleaning Previous Study " 
        if os.path.isdir(MSG.results_directory):
            for filepath in glob.glob("%s/*" % MSG.results_directory):
                    if os.path.isdir(filepath):
                        shutil.rmtree(filepath)
                    else:
                        os.remove(filepath)
        else:
            os.makedirs(MSG.results_directory)
        os.makedirs(MSG.results_directory+"/RESULTS")
        os.makedirs(MSG.results_directory+"/LOGS")


    #########################################################################
    # processing of the range of each varying index
    #########################################################################

    def process_indices(self, ind_typ):
        """set current indice values with the ones received"""
        ind, typ = ind_typ.split('___')
        set_flag("indices", ind.split('__'))
        self.initial_indices = ind.split('__')
        types = typ.split('__')
        for ind in range(len(types)):
            if types[ind] == 'int':
                self.initial_indices[ind] = int(self.initial_indices[ind])
            elif types[ind] == 'str':
                self.initial_indices[ind] = str(self.initial_indices[ind])
            elif types[ind] == 'float':
                self.initial_indices[ind] = float(self.initial_indices[ind])

    def return_range(self, *indices):
        """ return the set of indices to sweep at this level"""
        nb_var = len(indices)
        return self.sets[nb_var]

    def add_set(self, var_name, params):
        """ add a dimension to the sweeping"""
        self.vars.append(var_name)

        if type(params) == type([1, 2]):
            self.sets[self.nb_vars] = params
            self.calculate_index[self.nb_vars] = \
                        lambda *y:self.return_range(*y)
        else:
            self.calculate_index[self.nb_vars] = params
        self.nb_vars = self.nb_vars+1      


    def guess_result_dir_name(self,*values):

        if len(values)==len(self.vars):
            try:
                return self.calcul.result_dir_name(*values)
            except AttributeError:
                print "result_dir_name does not exist in Calcul object"
            except MyError, error:
                print "Unexpected error:", sys.exc_info()[0]
        s = "000_"
        for i in range(len(values)):
            s = s+"%s=%s__"%(self.vars[i],values[i])
        return s


    #########################################################################
    # wrapper calling the run method
    #########################################################################

    def run0(self, values):
        """ actually running the method of the calcul object"""
        self.values = values

        if len(values)!=len(self.vars):
            signal(ERROR, "pas assez de parametre ")
        else:
            self.values = values
            try:
                # result_directory
                self.result_dir_name = "%s/%s/RESULTS/%s" % \
                                       (MSG.maestro_directory,
                                        self.results_directory_relative_path,
                                        self.guess_result_dir_name(*self.values))
                # calling method run
                res = self.calcul.run(*self.values)
                sys.stdout.flush()

                # 
                set_flag("result", res)
                set_flag("status", "OK")
                set_flag("etat", "DONE")
            except MyError, error:
                set_flag("result", "Undetermined")
                set_flag("status", "ERROR : %s" % error)
                set_flag("etat", "DONE")


    #########################################################################
    # recursive sweeping of the definition domain
    #########################################################################


    def sweep_dim(self, dim, indices, action):
        """ recursively sweeping all dimensions of global domain """
        
        do_the_job = False
        if len(indices) == self.depth \
               or (self.depth == -1 and len(indices) == self.nb_vars):
            self.nb_job = self.nb_job+1
            if not(action == RUN):
                do_the_job = True

        if dim > 0 and not(do_the_job):

            #print range(self.set_dim[dim-1])
            #new_range = self.calculate_index(dim, indices)
            #f = lambda *x:self.return_range(*x)
            indices.reverse()
            new_range = self.calculate_index[self.nb_vars-dim](*indices)
            indices.reverse()
            for index in new_range:
                #print dim-1, index, self.sets[dim-1][index]
                indices.insert(0, index)
                set_flag('contexte', "%s_%s" % (get_flag('contexte'), index))
                #print get_flag('contexte')
                #print indices, dim, self.nb_job
                self.sweep_dim(dim-1,  indices, action)
                indices.pop(0)
        else:
            if (self.nb_job == self.my_job \
                or self.my_job == -1) or not(action == RUN):
                
                self.nb_jobs = self.nb_jobs+1
                save_env("sweeping")
                #print indices, self.nb_job, self.my_job, self.depth, sys.argv

                #GV.send_message("%s=%s"%(self.vars, indices))
                #print indices
                self.contexte = "__".join(map(lambda x:"%s" % x, indices))
                set_flag("contexte", self.contexte)
                set_flag("nb_job", self.nb_job)
                self.result_dir_name = "unknown_yet_%s" % self.contexte

                if action == RUN:
                    # actually running the calculation if not in the deployement
                    # step

                    
                    if get_flag("test_only"):
                        send_message("std",
                                "Should run(%s) in %s dir " \
                                % (self.contexte,
                                   get_flag("running_directory", 
                                   error_type = None)))
                    else:
                        self.create_tmp_file()

                        send_message("status", "%05d : Processing Job %05d      for %s in /%s@%s:%s " % \
                                     (self.nb_job, self.nb_job,
                                      self.contexte,
                                      get_flag('user_name'),
                                      MY_MACHINE_FULL_NAME,
                                      get_flag("running_directory")
                                      ), "G")
                        
                        self.temps_calcul = Timer(self.contexte)
                        self.temps_calcul.start()

                        indices.reverse()
                        os.chdir(get_flag("running_directory"))
                        self.run0(indices)
                        indices.reverse()

                        self.save_results_and_clean()

                        self.temps_calcul.stop()

                elif action == DEPLOY:
                    # launching job on cluster
                    types = ['xxx']*len(indices)
                    for i in range(len(indices)):
                        value = indices[i]
                        if type(value) == type(0):
                            types[i] = 'int'
                        elif type(value) == type("ss"):
                            types[i] = 'str'
                        elif type(value) == type(0.99):
                            types[i] = 'float'
                        else :
                            signal(CRITICAL, "%s type not spwanable!!!!"%value)

                    working_directory = get_flag("working_directory")

                    what = str.replace(self.results_directory_relative_path, " ", "_")

                    running_directory = str.replace('/%s/%s_%s/%s' % \
                                                    (working_directory, what, self.timestamp,self.nb_job), "//", "/")

                    set_flag("running_directory", running_directory)

                    command     = "mkdir -p %s \n chmod 700 %s \n echo . >  %s/output.log\n echo .>  %s/error.log\n" % \
                        (running_directory, running_directory, running_directory, running_directory)  \
                        +"cd %s/BUNDLE/Code\n" % MSG.results_directory \
                        +"python -u "+" ".join(sys.argv)+" --log_directory=%s " \
                        % MSG.results_directory+\
                        "--checksum_id=%s " % self.checksum_id+\
                        "--timestamp=%s " % self.timestamp+\
                        "--exec_job=%s --logto=%s::%s --project=%s " \
                        % (self.nb_job,self.logger_machine_name, self.logger_port,
                           self.jobname)
                
                    if not get_flag('gather'):
                        command = command + ">> %s/output.log 2> %s/error.log \n" % \
                            (running_directory, running_directory)
                    else:
                        command = command + "\n"


                    for keyword in ("kill", 
                                    "restart", "clean", "resume", "gather"):
                        command = str.replace(command, 
                                              "--%s" % keyword, "")
                    for keyword in (["procs","cores"]):
                        command = str.replace(command, 
                                              "--%s" % keyword, "--xxx")
                    command = "cd %s \n %s " % (self.starting_path, command) 
                    jobname_nb = "%s_%s" % (self.jobname, self.nb_job)
                    if get_flag("test_only"):
                        send_message("std", 
                                     "Should submit job %s with command =\n%s" \
                                     % (jobname_nb, command))
                    else:
                        if get_flag("debug") or True:
                            err_out_file = "%s/LOGS/%s_%s"%(get_flag("results_directory"),self.jobname,self.nb_job)
                            MY_LAUNCHER.submit(jobname_nb, 1, get_flag("wall-time-1-job"),
                                           command, "%s.out"%err_out_file , "%s.err"%err_out_file )
                        else:
                            MY_LAUNCHER.submit(jobname_nb, 1, get_flag("wall-time-1-job"),
                                           command, "/dev/null", "/dev/null")

                elif action == COUNT:
                    # nothing to do, only counting jobs!
                    types = ['xxx']*len(indices)
                    for i in range(len(indices)):
                        value = indices[i]
                        if type(value) == type(0):
                            types[i] = 'int'
                        elif type(value) == type("ss"):
                            types[i] = 'str'
                        elif type(value) == type(0.99):
                            types[i] = 'float'
                        else :
                            signal(CRITICAL, 
                                   "%s type not spawnable!!!!" % value)
                    ind = "%s___%s" % \
                            (("__".join(map(lambda x:"%s" % x, indices))), 
                              "__".join(types))
                    indices.reverse()
                    # result_directory
                    self.result_dir_name = "%s/%s/RESULTS/%s" % \
                                           (MSG.maestro_directory,
                                            self.results_directory_relative_path,
                                            self.guess_result_dir_name(*indices))
                                    
                    send_message("Jobs", 
                                 "Job_%s %s  %s " % \
                                 (self.nb_job, ind, self.result_dir_name),  "w")
                    indices.reverse()
                    if (math.floor((math.log10(self.nb_job+2)))-math.floor(math.log10(self.nb_job+1)))>0. :
                        self.count_print=True
                    if self.count_print and self.nb_job % 10 == 0:
                        self.count_print=False
                        send_message("std", 
                                     "\t%d Jobs counted so far." % self.nb_job)
                    self.job_indices[self.nb_job] = \
                        "__".join(map(lambda x:"%s" % x, indices))

                load_env("sweeping")

        if action == RUN \
               and (len(indices) == self.depth or \
                    (self.depth == -1 and len(indices) == self.nb_vars))\
               and (self.nb_job == self.my_job or self.my_job == -1):
            send_message("status", "%05d : Terminated --> %10s contexte %s results in %s calculation in /%s@%s:%s " % \
                    (self.nb_job,get_flag("status"),
                     get_flag("contexte",None),\
                     self.result_dir_name,
                     get_flag('user_name'), MY_MACHINE_FULL_NAME,\
                     get_flag("running_directory")), "G")


    #########################################################################
    # Initializing the sweeping process
    #########################################################################


    def sweep_domain(self):
      """ main method called to sweep domain"""
        
      try:

        GV.current_job = self
           
        print "\n\tsweeping the requested domain... \n"
             
        indices = self.initial_indices

        if len(indices):
            # performing a precise job
            # setting environment of calculation
            indices.reverse()
            for i in range(len(indices)-1):
                indices_so_far = indices[:i+1]
                self.calculate_index[i+1](*indices_so_far)
            indices.reverse()
            self.nb_job = self.my_job-1
            self.sweep_dim(self.nb_vars-len(indices), indices, RUN)
            set_flag("pinging", False)
            return 

        if self.my_job <= 0:

            # 1) evaluating total number of jobs first...
            # setting provisory the log dump directory

            set_flag("running_directory","%s/LOGS" % MSG.results_directory)

            self.sweep_dim(self.nb_vars-len(indices), indices, COUNT)
            send_message("Jobs", "Job_total %s " % self.nb_jobs, "w")
            time_str = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
            send_message("logger", "SUBMITTED PROCESS = %s jobs todo %s"  % \
                         (self.nb_jobs,time_str), "w")

            send_message("std", 
                         "\t%d Jobs counted." % self.nb_jobs)

            job_file = "%s/LOGS/Jobs.log" % MSG.results_directory
            shutil.copy(job_file,
                        "%s/BUNDLE/Jobs.log" % MSG.results_directory)
            self.nb_job_total = self.nb_jobs
            self.nb_job = 0

            # 1.1) if resuming...
            if get_flag("resume"):
                self.resume_all()

            if get_flag('make_jobs_list'):
                shutil.copy(job_file,"./JOBS_LIST")
		job_file="./JOBS_LIST"
                print "\n\t%d jobs created succesfully in file :"%self.nb_jobs
                print "\n\t\t",job_file
                self.kill_myself()

        if self.deploy_on_cluster_first:
            # deployement of the calculations on the nodes of a clusters

            message = "\n\tdeploying %d jobs on %s" % \
                            (self.nb_jobs, MY_MACHINE)
            send_message("std", message)

            # 3) ...then deploy

            self.nb_job = 0
            self.nb_jobs = 0

            if self.nb_procs:
                # a number of procs is given in the command line 
                # (--cores=nb_procs)
                # --> using avanti to deploy
		# --> dumping a command into an intermediate file 
                #             otherwise it's too big for mpirun command line
                working_directory = get_flag("working_directory")

                what = str.replace(self.results_directory_relative_path, " ", "_")

                running_directory = str.replace('/%s/%s_%s/$1' % \
                                                    (working_directory, what, self.timestamp), "//", "/")

                set_flag("running_directory", running_directory)

                # generic script job.cmd to run a single job
                # 3 parameters :
                #   $1 : elementary job number 
                #   $2 : name of the machine running the logger
                #   $3 : name of the logger port 
                if get_flag("debugoutput"):    
                    # debuggage... envoi des output dans ~/tmp
                    print "\t[DEBUG] sending job output into ~/tmp/... beware, results otained won't be moved to the regular RESULTS directory..."
                    running_directory = "~/%s" % running_directory
                todo     = "mkdir -p %s \nchmod 700 %s \necho . >  %s/output.log \necho .>  %s/error.log\n" % \
                           (running_directory, running_directory, running_directory, running_directory)  \
                          +"cd %s/BUNDLE/Code\n" % MSG.results_directory \
                          +"python -u "+" ".join(sys.argv)+" --log_directory=%s " \
                          % MSG.results_directory+\
                          "--checksum_id=%s " % self.checksum_id+\
                          "--timestamp=%s " % self.timestamp+\
                          "--exec_job=$1 --logto="+"$2::$3 --project=%s --server=$7 " \
                          % self.jobname
                
                todo = "export PYTHONPATH=%s\n" % os.getenv("PYTHONPATH") + todo
                # debugging

                
	        if not get_flag('gather'):
                    todo = todo + ">> %s/output.log 2> %s/error.log \n" % \
                       (running_directory, running_directory)
                else:
                    todo = todo + "\n"
                for keyword in (["procs","cores"]):
                    todo     = str.replace(todo, "--%s"%keyword, "--xxx")
                for keyword in ("kill", "restart", "resume", "clean", "gather"):
                    todo     = str.replace(todo, "--%s"%keyword, "")
                if get_flag("debugjobs"):
                    todo     = str.replace(todo, "--debugjobs","--debug")
                    
		filename_todo = "%s/LOGS/job.cmd" % get_flag("results_directory")
	        fic = open(filename_todo,"w")
		fic.write(todo)
		fic.close()


                # dedicated script logger.cmd to run a logger on the first node given
                # 2 parameters :
                #   $1 : elementary job number 
                #   $2 : coordinates of the logger place determined at the very beginning
                #        of the scheduled job pool
                logging_directory = "%s/LOGS/" % MSG.results_directory 
                
                pythonpath = os.getenv("PYTHONPATH")
                tolog     =   "export PYTHONPATH=%s\n \
                               mkdir -p %s \n echo . >  %s/logger_spawner_output.log\n \
                               echo .>  %s/logger_spawner_error.log\n" % \
                           (pythonpath,logging_directory, logging_directory, logging_directory)  \
                          +"cd %s/BUNDLE/Code\n" % MSG.results_directory \
                          +"python -u "+" ".join(sys.argv)+" --log_directory=%s " \
                          % MSG.results_directory+\
                          "--checksum_id=%s " % self.checksum_id+\
                          "--timestamp=%s " % self.timestamp+\
                          "--spawn_logger=%s " % MY_MACHINE + \
                          "--project=%s" % self.jobname
                if get_flag("sequential_job"):
                     tolog = tolog + " --launch_sequential_jobs"
                if get_flag("debuglogger"):
                    tolog = tolog + " --debug "
                tolog = tolog + ">> %s/logger_spawner_output.log 2> %s/logger_spawner_error.log \n" % \
                       (logging_directory, logging_directory)                
                for keyword in (["procs","cores"]):
                    tolog     = str.replace(tolog, "--%s"%keyword, "--xxx")
                for keyword in ("kill", "restart", "resume", "clean", "gather"):
                    tolog     = str.replace(tolog, "--%s"%keyword, "")

	        
		filename_tolog = "%s/LOGS/spawn_logger.cmd" % get_flag("results_directory")
	        fic = open(filename_tolog,"w")
		fic.write(tolog)
		fic.close()

                if get_flag("debuglogger"): 
                    print "[LOG] launch command for logger : />\n=====\n=====\n=====\n%s\n=====\n=====\n=====</ " % tolog



                if not get_flag("sequential_job"):
                    spawn_logger = "chmod 755 %s/LOGS/spawn_logger.cmd \nnohup '%s/LOGS/spawn_logger.cmd' & " % \
                                   (MSG.results_directory, MSG.results_directory)
                else:
                    spawn_logger = \
                                   """
cat > %s/LOGS/run_task.cmd << RUN_TASK_END
job=\$1
_SEQ_LAUNCHER_ << JOB_END
#!/bin/bash
cd %s; sh %s/LOGS/job.cmd \$job \$2 \$3
#sleep 10
JOB_END
RUN_TASK_END
chmod 755  %s/LOGS/run_task.cmd \n""" % (MSG.results_directory,self.starting_path,
                                       MSG.results_directory, MSG.results_directory)

                    spawn_logger = spawn_logger + \
                                   """
_SEQ_LAUNCHER_LOGGER_ << JOB_END
#!/bin/bash
chmod 755 %s/LOGS/spawn_logger.cmd
bash '%s/LOGS/spawn_logger.cmd'
JOB_END
                     """ % \
                                   (MSG.results_directory, MSG.results_directory)

                if get_flag("sequential_job"):
                    launch_jobs = "#!/bin/bash\n"
                    for nb_job in range(1,self.nb_job_total+1):
                        launch_jobs = launch_jobs + "%s/LOGS/run_task.cmd %d UNKNOWN UNKNOWN \n" % (MSG.results_directory,nb_job)
                        filename = "%s/LOGS/launch_jobs" % MSG.results_directory 
                        f = open(filename+".bash","w")
                        f.write(launch_jobs)
                        f.close()
                    spawn_logger = spawn_logger + \
                            """
# --------- lancement des jobs ----------------
sleep 10
chmod 755 %s.bash
bash %s.bash > %s.out  2> %s.err  """ % (filename,filename,filename,filename)
                else:
                    sleeping_time = 20
                    if MY_MACHINE=="localhost":
                        sleeping_time = 20
                    spawn_logger = spawn_logger + \
                                   "\nsleep %d; logger_name_port=`grep LOGGER_ADDRESS %s/LOGS/logger_spawner_output.log`" % \
                                   (sleeping_time, MSG.results_directory) + \
                                   "\ncommande=\"cd %s; bash %s/LOGS/job.cmd %%d  $logger_name_port\"" % \
                                   (self.starting_path, self.results_directory_relative_path)

                command = "$commande"


                # submitting  job lot through avanti
                if get_flag("test_only"):

                    # the submit is only scheduled 
                    # (--test is found in command line)
                    send_message("std",
                            "Should submit Avanti job %s on %d cores for \
                            %d jobs with \n\tcommand = %s \n\tspawn_logger = %s" \
                            % (self.jobname, self.nb_procs, 
                               self.nb_job_total, command,spawn_logger))
                else:
                    # actually launching it on nodes
                    test = Avanti(self.jobname, self.nb_procs, get_flag("wall-time-avanti-job"),
                                  MY_LAUNCHER, command, spawn_logger, self.nb_job_total,
                                  "%s/LOGS/job_all.out" % get_flag("results_directory"),
                                  "%s/LOGS/job_all.err" % get_flag("results_directory"),)
                    test.run()
            else:
                # launching each job separately
                # ...deployment process is taken in charge 
                # in sweep_dim recursive method
                self.sweep_dim(self.nb_vars-len(indices), indices, DEPLOY)

        else:
#            try:
            self.sweep_dim(self.nb_vars, indices, RUN)
#            except:
#                raise MyError("exception raised")
#                
            #self.bilan()
            self.save_results_and_clean() 
        

        set_flag("pinging", False)

        if not (MY_MACHINE=="localhost" and self.nb_procs<1):
            print "\n\tYour job has been submitted... \
            \n\n\tYou can check its status by issuing the command:"
            print "\t\tpython", " ".join(sys.argv[:1]), " --status ",get_flag("result")


        return self.nb_jobs

      except:
        #print 'ici'
        self.result_dir_name = "%s/%s/RESULTS/%s" % \
                               (MSG.maestro_directory,
                                self.results_directory_relative_path,
                                            self.guess_result_dir_name(*indices))
        message_start = " \n\n%s\n ERROR occured on \
                          \n\t machine: %s\
                          \n\t contexte: %s\
                          \n\t result directory: %s \
                          \n%s \n\t" % \
                          ("v"*80, 
                           MY_MACHINE_FULL_NAME,
                           get_flag('contexte',None),
                           self.result_dir_name,
                           "^"*80)

        message_end = " %s\n\n" % ("v"*80)

                                    

        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        
        if get_flag("my_job")>-1:
            print message_start
            traceback.print_exception(exceptionType,exceptionValue, exceptionTraceback,\
                                  file=sys.stdout)
            print message_end
        
        print >> sys.stderr, message_start
        traceback.print_exception(exceptionType,exceptionValue, exceptionTraceback,\
                                  file=sys.stderr)
        print >> sys.stderr, message_end
        
        send_message("status", "%05d : Terminated  --> %10s results in %s for %s in /%s@%s:%s" % \
                     (self.nb_job,"CRITICAL",\
                      self.result_dir_name, \
                      get_flag("contexte",None),\
                      get_flag('user_name'), MY_MACHINE_FULL_NAME,\
                     get_flag("running_directory")), "G")
        self.save_results_and_clean(take_all=True)

        self.kill_myself()
        
    def __del__(self):
        
        if get_flag("my_pid"):
            send_message("process" ,"%s ENDED" % get_flag("my_pid"))

    #########################################################################
    # management of the temporary running environment
    #########################################################################

    def create_tmp_file(self):
        """ creation of the working directory"""
        # Creation du repertoire de travail

        current_job = get_flag("nb_job")
        working_directory = get_flag("working_directory")

        what = str.replace(self.results_directory_relative_path, " ", "_")
        running_directory = str.replace('/%s/%s_%s/%s' % \
                                            (working_directory, what, self.timestamp,current_job), "//", "/")
        
        set_flag("running_directory", running_directory)
        if (str.find(running_directory, TMPDIR) == -1):
            signal(CRITICAL, 
                   "running_directory=%s was to be erased!!!" %\
                    running_directory)
        else:
            if (os.path.isdir(running_directory)):
                for filepath in glob.glob("%s/*" % running_directory):
                    if os.path.isdir(filepath):
                        shutil.rmtree(filepath)
                    else:
                        (dirname, filename)=os.path.split(filepath)
                        if not (filename=="error.log" or filename=="output.log" or filename=="install.log"):
#                             if get_flag('debug'):
#                                 send_message("removed"," %s remove file %s" % \
#                                              (MY_MACHINE_FULL_NAME, filepath), "G")
                            os.remove(filepath)
            try:
                os.makedirs(running_directory)
                os.chmod(running_directory,0o700)
                
            except:
                pass

    def save_results_and_clean(self, take_all=False):
        """ sauvegarde des resultats obtenus en fin de job"""

        if get_flag('debug'):
            print "[DEBUG] save_results_and_clean called from directory: ",os.getcwd()
            print "[DEBUG] Files to save in RESULTS:",self.calcul.get_saved_files()

        if len(self.calcul.get_saved_files()) == 0:
            return

        already_saved = {}

        # sauvegarde des resultats obtenus
        current_job = get_flag("nb_job")
        contexte = get_flag("contexte")
        target_dir = self.result_dir_name
        if get_flag('debug'):
            print "[DEBUG] RESULT directory:",target_dir
        if not os.path.isdir(target_dir):
            try:
                os.makedirs(target_dir)
            except:
                pass   # directory created by another process -> no pb!!!

        if get_flag('debug'):
            linking_file = "%s/From_Job_%s_at_%s:%s"\
                         % (target_dir, get_flag("nb_job"),
                           MY_MACHINE_FULL_NAME,
                           get_flag("contexte"))
    
            # touching file indicating the working directory path
            fic = open(linking_file, "a")
            fic.write("/%s@%s:%s " % \
                        (get_flag('user_name'), MY_MACHINE_FULL_NAME,\
                         get_flag("running_directory")))
            fic.close()
        
        to_save = self.calcul.get_saved_files()
        to_save.append("*.log")
        if take_all:
            to_save = "*"
        for pattern in to_save:
            full_path_pattern = get_flag("running_directory")+'/'+pattern
            if get_flag('debug'):
                print "[DEBUG] searching for pattern:",full_path_pattern
            for fic in glob.glob(full_path_pattern):
                if not fic in already_saved.keys():
                    if get_flag('debug'):
                        print "trying to save :",fic
                    (dirname, filename)=os.path.split(fic)
                    fic_dest = '%s/%s' % (target_dir, filename)
                    if os.path.isfile(fic) and fic!=fic_dest:
                        shutil.copy(fic,fic_dest)
                    if os.path.isdir(fic) and fic!=fic_dest:
                        shutil.copytree(fic, fic_dest, symlinks=False, ignore=None)
                    already_saved[fic]=1
                
                    
                    
        if not(get_flag("logger_name")):
          sys.stdout.dump("%s/output.log"%target_dir)
          sys.stderr.dump("%s/error.log" % target_dir)

        if not get_flag('nocleaning'):
            # cleaning working directory
            try:
                shutil.rmtree(get_flag("running_directory"))
            except:
                pass
             

class Study(Job):

    def add_sweep_dimension(self, var_name, params):
        return Job.add_set(self, var_name, params)


welcome_message()
