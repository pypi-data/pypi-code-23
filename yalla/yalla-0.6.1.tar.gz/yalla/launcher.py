#-*-coding:iso-8859-1-*- 
#!/logiciels/public/bin/python-2.4
#
#
"""
module interfacing calls from maestro
with the machine:cluster it's running on
"""

import subprocess, os




from messages import send_message, get_flag, signal, CRITICAL
from env      import MY_MACHINE, SCHEDULER

LAUNCHERS = {}

SUBMITTED = "SUBMITTED"

MY_LAUNCHER = None


class Launcher:
    """
    Generic launcher class
    to interface maestro with the scheduler
    """
    def __init__(self, procs_per_node, sub, seq_sub, \
                     resa, cancel, status, probe, seq_queue, \
                     submit_background=" ",seq_sub_logger=None, seq_sub_timed=None ):

        self.ongoing_jobs = {}

        self.sub = sub
        self.seq_sub = seq_sub

        if seq_sub_logger:
            self.seq_sub_logger = seq_sub_logger
        else:
            self.seq_sub_logger = seq_sub

        if seq_sub_timed:
            self.seq_sub_timed = seq_sub_timed
        else:
            self.seq_sub_timed = seq_sub
            
        self.seq_queue = seq_queue 
        self.resa = resa
        self.probe = probe
        self.cancel = cancel
        self.status = status
        self.procs_per_node = procs_per_node
        self.submit_background = submit_background 

    def run(self, command):
        """ execute a command """
        #send_message("deploy", "launching command : \n %s"%command)
        if get_flag("debug"):
            send_message("std", "\nlaunching command : \n %s" % command)
        os.system(command)
        return "none"

    def submit(self, job_name, nb_procs, wallclock_time, job_file, output, error):
        """ submit a job with given paramaters """

        if get_flag("debug"):
            print "submit parameter : job_name=/%s/, nb_procs=/%s/, wallclock_time=/%s/, job_file=/%s/, output=/%s, error=/%s/" % \
                  (job_name, nb_procs, wallclock_time, job_file, output, error)

        ppn = get_flag("ppn")
        if not(ppn):
            ppn = self.procs_per_node
        ppn = int(ppn)

        nb_nodes = nb_procs/ppn+min(1,nb_procs % ppn)
        nb_cpus = min(nb_nodes, ppn)
        account = get_flag("account")
        if get_flag("debug"):
            print "nb_cpus=/%s/ nb_procs=/%s/ procs_per_nodes=/%s" % (nb_cpus,nb_procs,ppn)
   
        if not(wallclock_time): # sequential job
            sub = self.seq_sub
            sub = str.replace(sub, "_QUEUE_", self.seq_queue)
            (h,m,s) = str(wallclock_time).split(':')
            cpu_time = "%s:%s:%s" % (h,m,s)
            sub = str.replace(sub,  "_CPUTIME_", str(cpu_time))
        elif get_flag("reservation"):
            sub = self.resa
            sub = str.replace(sub,  "_RESERVATION_", get_flag("reservation"))
        else:
            sub = self.sub


        if get_flag("debug"):
            print "----------  sub before -----------------\n%s\n------------------"%sub

        if wallclock_time: # non sequential job
            (h,m,s) = str(wallclock_time).split(':')
            #cpu_time = "%s:%s:%s" % (int(h)*nb_procs,m,s)
            cpu_time = "%s:%s:%s" % (h,m,s)
            sub = str.replace(sub,  "_TIME_", str(wallclock_time))
            sub = str.replace(sub,  "_CPUTIME_", str(cpu_time))
            sub = str.replace(sub,  "_CPUS_", str(nb_cpus))


        if get_flag("sequential_job"):
            # processing of job_file to replace submit sequentiel
            f = open(job_file,"r")
            job_content = "".join(f.readlines())
            f.close()
            # sequential job specific substitutions
            # logger only
            job_content = job_content.replace("_SEQ_LAUNCHER_LOGGER_",self.seq_sub_logger)
            job_content = str.replace(job_content, "_OUTPUT_", output+"_logger")
            job_content = str.replace(job_content, "_ERROR_", error+"_logger")
            job_content = str.replace(job_content, "_NAME_", job_name[:-4]+"_log")
            # other tasks
            if get_flag("time_flag"):
                job_content = job_content.replace("_SEQ_LAUNCHER_",self.seq_sub_timed)
            else:
                job_content = job_content.replace("_SEQ_LAUNCHER_",self.seq_sub)
            if get_flag("debug"):
                job_content = str.replace(job_content, "_OUTPUT_", output+"_\\$job")
                job_content = str.replace(job_content, "_ERROR_", error+"_\\$job")
            else:
                job_content = str.replace(job_content, "_OUTPUT_", "/dev/null")
                job_content = str.replace(job_content, "_ERROR_",  "/dev/null")
            
            job_content = str.replace(job_content,  "_NODES_", str(1))
            job_content = str.replace(job_content,  "__TASKS__", str(nb_procs))
            job_content = str.replace(job_content,  "_PPN_", str(1))
            job_content = str.replace(job_content, "_NAME_", job_name)
            job_content = str.replace(job_content,  "NPP=", "NPP=3  #NPP")
            job_content = str.replace(job_content,  "mpirun", "#mpirun")
            job_content = str.replace(job_content,  'cat $PBS', "#cat PBS")
            job_content = str.replace(job_content,  '_CPUTIME_', str(cpu_time))
            job_content = str.replace(job_content,  "__ACCOUNT__", str(account))
            f = open(job_file,"w")
            os.rename(job_file,job_file+"2")
            f = open(job_file,"w")
            f.write(job_content)
            f.close()
            sub = "bash"
        else:
                # processing of job_file to replace submit sequentiel
            f = open(job_file,"r")
            job_content = "".join(f.readlines())
            f.close()
            job_content = str.replace(job_content,  '__JOB_NAME__', job_name)
            job_content = str.replace(job_content,  '__CPUTIME__', str(cpu_time))
            job_content = str.replace(job_content,  "__NODES__", str(nb_nodes))
            job_content = str.replace(job_content,  "__TASKS__", str(nb_procs))
            job_content = str.replace(job_content,  "__ACCOUNT__", str(account)) 
            job_content = str.replace(job_content,  "__PPN__", str(ppn))
            f = open(job_file,"w")
            f.write(job_content)
            f.close()

        # substitutions not made yet, to be done now after specific sequential processing
        sub = str.replace(sub,  "_NODES_", str(nb_nodes))
        sub = str.replace(sub, "__TASKS__", str(nb_procs))
        sub = str.replace(sub,  "_PPN_", str(min(ppn,nb_procs)))
        sub = str.replace(sub, "_OUTPUT_", output)
        sub = str.replace(sub, "_ERROR_", error)
        sub = str.replace(sub, "_NAME_", job_name)

        if get_flag("debug"):
            print "----------  sub after -----------------\n%s\n------------------"%sub


        if os.path.isfile(job_file):
            job_id = self.run("cd %s; %s %s >> /dev/null 2>&1 %s" % \
                              (get_flag("results_directory"), sub, job_file,self.submit_background))
        else:    
            job_id = self.run("cd %s; cat > %s/job_seq_%s << EOF   \n" % \
                              (get_flag("results_directory"), get_flag("results_directory"), get_flag("nb_job"))\
                              +"#!/bin/sh\n %s\nEOF\n %s %s  %s/job_seq_%s >> /dev/null 2>&1  " % \
                              ( job_file,self.submit_background, sub, get_flag("results_directory"),get_flag("nb_job"))) 
        self.ongoing_jobs[job_id] = SUBMITTED

    def get_stat(self, job_name):
        """ get statistics on an ongoing job"""
        command = ("%s " % self.probe) % get_flag('user_name')
        if get_flag("debug"):
            print job_name, command
        fic = os.popen(command)
        res = fic.readlines()
        fic.close()
        return res
    
    def stat(self, job_name, verbose=True):
        """ get statistics"""
        
        res = self.get_stat(job_name)
        
        nb_process = 0
        logger = 0
        for ligne in res:
            if str.find(ligne, job_name[:8]) >= 0 :
                if get_flag("debug"):
                    print ligne[:-1]
                if str.find(ligne,"logserver.py")==-1 and str.find(ligne,"_log")==-1:
                    nb_process =  nb_process+1
                else:
                    logger = 1
        if verbose:
            if logger:
                print "Logger is OK"
            else:
                print "No logger running... (OK if job done) "
            print nb_process," process currently running..."
        return nb_process
        
    def get_status(self, job_name):
        """ get status of an ongoing job"""
        command = self.status % (get_flag('user_name'),job_name[:9])
        if get_flag("debug"):
            print command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        os.waitpid(process.pid, 0)
        output = process.stdout.read().strip()
        if get_flag("debug"):
            print output
        return output
            

    def kill(self, job_name):
        """ kill an ongoing job"""
        command = self.cancel % (get_flag('user_name'),job_name[:9])
        if get_flag("debug"):
            print command
        os.system(command)
            
    
LAUNCHERS_CMD = { 
  "pbscla2" : \
    { "sub"    : " qsub  -N _NAME_ -l nodes=_NODES_:ppn=_PPN_,walltime=_CPUTIME_" \
                    + " -o _OUTPUT_ -e _ERROR_", \
      "seq_sub" : " qsub -q seq_moyen -N _NAME_ -o _OUTPUT_ -e _ERROR_", \
      "seq_sub_timed" : " qsub -l walltime=_CPUTIME_ -N _NAME_ -o _OUTPUT_ -e _ERROR_", \
      "seq_sub_logger" : " qsub -q seq_long -N _NAME_ -o _OUTPUT_ -e _ERROR_", \
      "resa"   : " qsub  -l advres=_RESERVATION_ " \
                    + "-N _NAME_ -l nodes=_NODES_:ppn=_PPN_,cput=_CPUTIME_" \
                    + " -o _OUTPUT_ -e _ERRROR_",\
      "cancel" : "/usr/sbin/qstat.rootonly | grep %s | grep %s |" \
                    + " awk '{  print \"qdel \",$1}' | /bin/sh",\
      "status" : "/usr/sbin/qstat.rootonly | grep %s | grep %s |" \
                    + " awk '{ print $(NF-1)}' ",\
      "probe"  : "/usr/sbin/qstat.rootonly -u %s"}, \
  "pbs" : \
    { "sub"    : " qsub  -N _NAME_ -l nodes=_NODES_:ppn=_PPN_,walltime=_CPUTIME_" \
                    + " -o _OUTPUT_ -e _ERROR_", \
      "seq_sub" : " qsub  -N _NAME_ -o _OUTPUT_ -e _ERROR_", \
      "resa"   : " qsub  -l advres=_RESERVATION_ " \
                    + "-N _NAME_ -l nodes=_NODES_:ppn=_PPN_,cput=_CPUTIME_" \
                    + " -o _OUTPUT_ -e _ERRROR_",\
      "cancel" : "qstat | grep %s | grep %s |" \
                    + " awk '{  print \"qdel \",$1}' | /bin/sh",\
      "status" : "qstat | grep %s | grep %s |" \
                    + " awk '{ print $(NF-1)}' ",\
      "probe"  : "qstat -u %s"}, \
  "slurm" : \
    { "sub"    : " sbatch -J _NAME_ --time _CPUTIME_",
      "seq_sub" : " sbatch -J _NAME_ -o _OUTPUT_ -e _ERROR_", \
      "resa"   : " qsub  -l advres=_RESERVATION_ " \
                    + "-N _NAME_ -l nodes=_NODES_:ppn=_PPN_,cput=_CPUTIME_" \
                    + " -o _OUTPUT_ -e _ERRROR_",\
      "cancel" : "squeue  -o  '%%.7i %%.9P %%.18j %%.8u %%.8T %%.9l %%.10M %%.6D '| grep %s | grep %s |" \
                    + " awk '{  print \"scancel \",$1}' | /bin/sh",\
      "status" : "squeue -o  '%%.7i %%.9P %%.18j %%.8u %%.8T %%.9l %%.10M %%.6D '| grep %s | grep %s |" \
                    + " awk '{ print $5}' ",\
      "probe"  : "squeue -o  '%%.7i %%.9P %%.18j %%.8u %%.8T %%.9l %%.10M %%.6D '| grep %s"}, \
  "loadleveler" : \
    { "sub"    : " llsubmit ",
      "seq_sub" : " sbatch -J _NAME_ -o _OUTPUT_ -e _ERROR_", \
      "resa"   : " qsub  -l advres=_RESERVATION_ " \
                    + "-N _NAME_ -l nodes=_NODES_:ppn=_PPN_,cput=_CPUTIME_" \
                    + " -o _OUTPUT_ -e _ERRROR_",\
      "cancel" : "llq -f %%id %%jn %%o %%dq %%st %%BS %%c %%h -u %s | grep %s |" \
                    + " awk '{  print \"llcancel \",$1}' | /bin/sh",\
      "status" : "llq | grep %s | grep %s |" \
                    + " awk '{ print $5}' ",\
      "probe"  : "llq | grep %s"}, \
   "unix" : \
    {"sub"     : "nohup sh ", 
     "seq_sub" : "nohup sh ", 
     "resa"    : "nohup sh ",
     "cancel"  : "ps -edf --width=500 | grep %s | grep %s |" \
                    +" awk '{ print \"kill -9 \",$2 }' | /bin/sh > /dev/null 2>&1",\
     "status"   : "ps -edf --width=500 | grep %s |grep python |"\
                    +" grep -v 'sh -c cd' | grep -v avanti.exe && echo %s > /dev/null", 
     "probe"   : "ps -edf --width=500 | grep %s |grep python |"\
                    +" grep -v 'sh -c cd' | grep -v avanti.exe", 
      "submit_background" :"&" }
  }



debug=False


def set_scheduler(my_machine):
    global MY_LAUNCHER, SCHEDULER, LAUNCHERS_CMD
    if my_machine in SCHEDULER.keys():
        MY_SCHEDULER, MY_NBPROCS, MY_SEQ_QUEUE = SCHEDULER[my_machine]
        if debug:
            print my_machine
            print "Scheduler associe : ",MY_SCHEDULER,MY_NBPROCS
        if MY_SCHEDULER in LAUNCHERS_CMD.keys():
            parameters =  LAUNCHERS_CMD[MY_SCHEDULER]
            parameters.update( {"procs_per_node":MY_NBPROCS})
            parameters.update( {"seq_queue":MY_SEQ_QUEUE})
            if debug:
                print parameters
            my_launcher = Launcher(**parameters)
            return my_launcher

MY_LAUNCHER=set_scheduler(MY_MACHINE)

if __name__ == "__main__":
    MY_LAUNCHER.submit("essai", 2, 2, "beep")
