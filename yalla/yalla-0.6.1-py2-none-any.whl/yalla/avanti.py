#-*-coding:iso-8859-1-*-
#!/logiciels/public/bin/python-2.4

"""
module launching processes on a given number of nodes using
MPI library
"""

import os


from calcul import Calcul
from messages import CRITICAL, send_message, signal, \
    get_flag, set_balises
from launcher import LAUNCHERS
from env import MY_MACHINE

class Avanti(Calcul):
    """
    class spawning calculation over a set of processors
    tied together through MPI.
    """


    def __init__(self,
                 job_name, nb_procs, cpu_time,
                 launcher, commande, spawn_logger, nb_jobs, output, error):

        Calcul.__init__(self, "avanti") 
        self.launcher = launcher
        self.nb_procs = nb_procs
        self.cpu_time = cpu_time
        self.job_name = job_name
        self.output = output
        self.error  = error

        self.machine = MY_MACHINE
        self.avanti_dir = get_flag("maestro_directory")+"/maestro/avanti"
        MAESTRO_PATH = os.getenv("MAESTRO_PATH")
        if not(MAESTRO_PATH):
            MAESTRO_PATH = "/opt/slurm/etc/maestro/1.5"
            print "\n\t!!! MAESTRO_PATH forced at ",MAESTRO_PATH

        self.avanti_dir = "%s/maestro/avanti" % MAESTRO_PATH

        # fixing home bug on rendvous
        commande = str.replace(commande, "home02", "home")
        spawn_logger = str.replace(spawn_logger, "home02", "home")


        debug = ""
        avanti_output = "%s/LOGS/job.out" % get_flag("results_directory")
        avanti_error = "%s/LOGS/job.err" % get_flag("results_directory")
        avanti_detail_output = "/dev/null"
        avanti_detail_output = "%s/LOGS/job.out" % get_flag("results_directory")
        if get_flag("debug"):
            debug = "debug"
            avanti_detail_output = "%s/LOGS/job_debug.out" % \
                                   get_flag("results_directory")
        
        set_balises(__AVANTI_PATH__ = self.avanti_dir, 
                   __COMMANDE__ = commande, 
                   __SPAWN_LOGGER__ = spawn_logger, 
                   __NB_JOBS__ = nb_jobs, 
                   __STARTING_PATH__ = get_flag("maestro_directory"), 
                   __RESULTS_PATH__ = get_flag("results_directory"), 
                   __PARALLEL_RUNS__ = get_flag("tasks-per-job"), 
                   __QUEUE__ = get_flag("queue"),
                   __NB_PROCS__ = self.nb_procs, 
                   __DEBUG__ = debug, 
                   __PYTHONPATH__ = os.getenv('PYTHONPATH'),
                   __AVANTI_OUTPUT__ = avanti_output, 
                   __AVANTI_ERR__ = avanti_error, 
                   __AVANTI_DETAIL_OUTPUT__ = avanti_detail_output)

        avanti_job_template = "%s/job.%s" % (self.avanti_dir, self.machine)

        self.job_avanti = "%s/LOGS/job.sub" % get_flag("results_directory")

        if get_flag("debug"):
            print "self.job_avanti=/%s/, avanti_job_template=/%s/" % (self.job_avanti, avanti_job_template)
        self.set_input_file(self.job_avanti, avanti_job_template, 
		            ["__AVANTI_PATH__", "__COMMANDE__",
                             "__NB_JOBS__", "__STARTING_PATH__", 
                             "__NB_PROCS__", "__DEBUG__",
                             "__AVANTI_OUTPUT__", "__AVANTI_DETAIL_OUTPUT__"])
        
        # checking if avanti is unabled on this machine 
        if not os.path.isfile(avanti_job_template):
            signal(CRITICAL,
                   "avanti not available on %s ... \
                   no avanti job template for this type of machine" \
                   % self.machine+'/'+avanti_job_template)
        makefile_name = "%s/Makefile.%s" % (self.avanti_dir, self.machine)
        if not os.path.isfile(makefile_name):
            signal(CRITICAL,
                   "avanti not available on %s ... \
                   no makefile available for this type of machine" \
                   % self.machine) 

        # compilation of avanti
        os.system("cd %s; make -f Makefile.%s > %s/LOGS/job.out 2>&1" \
                  % (self.avanti_dir, self.machine, get_flag('results_directory')))
        
    def run(self):
        """
        running/submitting the complete sequence of job
        through an MPI Master/Worker program running on nb_procs nodes
        """

        self.prepare()

        self.launcher.submit(self.job_name, self.nb_procs,
                             self.cpu_time, self.job_avanti,
                             self.output,   self.error)


if __name__ == "__main__":
	
    TEST = Avanti("essai", 2, "4:00", LAUNCHERS["pbs"], "touch hello_%d", 7)
    TEST.run()
