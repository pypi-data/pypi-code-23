#!/usr/bin/env python

import time,sys
import os,thread
import pp

command_template = sys.argv[1]
nb_total_jobs= int(sys.argv[2])
nb_procs = int(sys.argv[3])
machines_file=sys.argv[4]


def execute(command_template,num):
    """executing a command"""
    command = command_template % num
    print "executing ",command
    os.system(command)
    return 0

starting_path = os.getcwd()

# Create jobserver
fic = open(machines_file)
machines_names = fic.readlines()
print 'machines_names',machines_names
machines=()
already={}
for m in machines_names:
    m=m[:-1]
    if not m[:9]=="localhost":
        if not m in already.keys():
            already[m]=1
            machines = machines+ (m,)
        else:
            already[m]=already[m]+1

nb=0
# for m in already.keys():
#     machines = machines+ (m,)
#     command = "nohup ssh %s 'python -u %s/maestro/pp/ppserver.py -a -t 20 -w %s -s master -y %s  '&" % (m,MAESTRO_PATH,"%s"% already[m] ,nb)
#     nb=nb+1
#     print "executing on %s: %s" % (m,command)
#     os.system(command)

MAESTRO_PATH = "/opt/share/maestro/1.4.1/"
print "\n\t!!! in pp/avanti.py MAESTRO_PATH forced at ",MAESTRO_PATH

for m in already.keys():
    for nb_serv in range(already[m]):
        command = "nohup ssh %s 'python -u %s/maestro/pp/ppserver.py -a -t 20 -w %s -s master -y %s  '&" % (m,MAESTRO_PATH,"1",nb)
        nb=nb+1
        print "executing on %s: %s" % (m,command)
        os.system(command)

print 'machines',machines


# Create jobserver
job_server = pp.Server(ncpus=0,ppservers=machines,secret="master")

print "running '%s' for %d jobs with %s procs" % (command_template,nb_total_jobs,nb_procs)

# Execute the same task with different amount of active workers and measure the time


if len(machines)==0:
    job_server.set_ncpus(int(nb_procs))

start_time = time.time()
print "Starting ", job_server.get_ncpus(), " workers"
for job_nb in xrange(nb_total_jobs):
    print "running job #%s"%job_nb,command_template,job_nb+1
    job_server.submit(execute, (command_template, job_nb+1), group="avanti")
job_server.wait(group="avanti")

print "Time elapsed: ", time.time() - start_time, "s"

print
job_server.print_stats()

# Parallel Python Software: http://www.parallelpython.com
