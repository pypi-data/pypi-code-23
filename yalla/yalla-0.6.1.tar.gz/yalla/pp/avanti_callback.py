#!/usr/bin/env python

import time,sys, thread
import os
import pp

command_template = sys.argv[1]
nb_total_jobs= int(sys.argv[2])
nb_procs = int(sys.argv[3])

command = {}

mainlock = thread.allocate_lock()

def execute(command):
    """executing a command"""
    mainlock.acquire()
    print "running ",command
    os.system(command)
    mainlock.release()
    return 0



#class for callbacks
class Moteur:


    def __init__(self,job_server, command_template, nb_total_jobs):
        self.current_job = 0
        self.nb_jobs_done = 0
        self.job_server = job_server
        self.command_template = command_template
        self.nb_total_jobs = nb_total_jobs
        self.completre = False
        
    def jobDone(self):
        mainlock.acquire()
        self.nb_jobs_done += 1
        self.complete = self.nb_jobs_done == self.nb_total_jobs
        mainlock.release()
        if self.complete:
            print "every job done"
            self.job_server.print_stats()
        else:
            self.nextJob()
        
    def nextJob(self):
        global execute
        print "in nextJob"
        run = False
        mainlock.acquire()
        self.current_job += 1
        if self.current_job <= self.nb_total_jobs:
            run = self.current_job
        mainlock.release()
        if run:
            print "running job #%s"%run
            command = self.command_template % (run)
            print "executing ",command
            self.job_server.submit(execute, (command,run), group="avanti", callback=self.jobDone())




starting_path = os.getcwd()

# Create jobserver
fic = open("machines.txt")
machines_names = fic.readlines()
machines=[]
already={}
for m in machines_names:
    m=m[:-1]
    if not m in already.keys() and not m[:9]=="localhost":
        already[m]=1
        machines.append(m)
        command = "nohup rsh %s 'python /home/kortas/TSAR3D/maestro/pp/ppserver.py -a -t 30  '&" % (m)
        print "executing on %s: %s" % (m,command)
        os.system(command)

print tuple(machines[1:])

# Create jobserver
job_server = pp.Server(ppservers=tuple(machines[1:]))

print "running '%s' for %d jobs with %s procs" % (command_template,nb_total_jobs,nb_procs)

# Execute the same task with different amount of active workers and measure the time

job_server.set_ncpus(int(nb_procs))

start_time = time.time()
print "Starting ", job_server.get_ncpus(), " workers"

moteur = Moteur(job_server, command_template, nb_total_jobs)

# premiere salve de jobs
for job_nb in xrange(min(nb_procs,nb_total_jobs)):
    moteur.nextJob()

while not(moteur.complete):
    time.sleep(1)
    
print "Time elapsed: ", time.time() - start_time, "s"

print

# Parallel Python Software: http://www.parallelpython.com
