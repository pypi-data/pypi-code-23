#!/usr/bin/env python
# File: dynamic_ncpus.py
# Author: Vitalii Vanovschi
# Desc: This program demonstrates parallel computations with pp module 
# and dynamic cpu allocation feature.
# Program calculates the partial sum 1-1/2+1/3-1/4+1/5-1/6+... (in the limit it is ln(2))
# Parallel Python Software: http://www.parallelpython.com

import math, sys, time, thread
import os
import pp

#class for callbacks
class Sum:
    def __init__(self):
        self.value = 0.0
        self.lock = thread.allocate_lock()
        self.count = 0

    #the callback function
    def add(self, value):
        # we must use lock here because += is not atomic
        self.count += 1
        self.lock.acquire()
        self.value += value
        print "in callback : value=%s"%value
        self.lock.release()
        
def part_sum(start, end):
    """Calculates partial sum"""
    sum = 0
    for x in xrange(start, end):
        if x % 2 == 0:
           sum -= 1.0 / x 
        else:
           sum += 1.0 / x 
    return sum

print """Usage: python dynamic_ncpus.py"""
print 

start = 1
end = 20000000

# Divide the task into 64 subtasks
parts = 64
step = (end - start) / parts + 1

# Create jobserver
fic = open("machines.txt")
machines_names = fic.readlines()
machines=[]
already={}
for m in machines_names:
    m=m[:-1]
    if not m in already.keys():
        already[m]=1
        machines.append(m)
        command = "nohup rsh %s 'python /home/kortas/TSAR3D/maestro/pp/ppserver.py -a -t 10 '&" % m
        print "executing on %s: %s" % (m,command)
        os.system(command)

print tuple(machines[:-1])

# Create jobserver
job_server = pp.Server(ppservers=tuple(machines))

# Create anm instance of callback class
sum = Sum()

# Execute the same task with different amount of active workers and measure the time
start_time = time.time()
for index in xrange(parts):
    starti = start+index*step
    endi = min(start+(index+1)*step, end)
    # Submit a job which will calculate partial sum 
    # part_sum - the function
    # (starti, endi) - tuple with arguments for part_sum
    # callback=sum.add - callback function
    job_server.submit(part_sum, (starti, endi), callback=sum.add)
  
#wait for jobs in all groups to finish 
job_server.wait()
    
# Print the partial sum
print "Partial sum is", sum.value, "| diff =", math.log(2) - sum.value

job_server.print_stats()

# Parallel Python Software: http://www.parallelpython.com
