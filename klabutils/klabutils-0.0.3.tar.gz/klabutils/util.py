import time
from subprocess import Popen, PIPE
import os
import numpy as np

class GPU:
    def __init__(self, ID, load, memoryTotal, memoryUsed, memoryFree, driver, gpu_name, serial, display_mode, display_active):
        self.id = ID
        self.load = load
        self.memoryUtil = float(memoryUsed)/float(memoryTotal)
        self.memoryTotal = memoryTotal
        self.memoryUsed = memoryUsed
        self.memoryFree = memoryFree
        self.driver = driver
        self.name = gpu_name
        self.serial = serial
        self.display_mode = display_mode
        self.display_active = display_active

def showUtilization(all=False):
    GPUs = getGPUs()
    if (all):
        print(' ID | Name | Serial || GPU util. | Memory util. || Memory total | Memory used | Memory free || Display mode | Display active |')
        print('------------------------------------------------------------------------------------------------------------------------------')
        for gpu in GPUs:
            print(' {0:2d} | {1:s}  | {2:s} || {3:3.0f}% | {4:3.0f}% || {5:.0f}MB | {6:.0f}MB | {7:.0f}MB || {8:s} | {9:s}'.format(gpu.id,gpu.name,gpu.serial,gpu.load*100,gpu.memoryUtil*100,gpu.memoryTotal,gpu.memoryUsed,gpu.memoryFree,gpu.display_mode,gpu.display_active))
    else:
        print(' ID  GPU  MEM')
        print('--------------')
        for gpu in GPUs:
            print(' {0:2d} {1:3.0f}% {2:3.0f}%'.format(gpu.id, gpu.load*100, gpu.memoryUtil*100))

def safeFloatCast(strNumber):
    try:
        number = float(strNumber)
    except ValueError:
        number = float('nan')
    return number

def getGPUs():
    # Get ID, processing and memory utilization for all GPUs
    p = Popen(["nvidia-smi","--query-gpu=index,utilization.gpu,memory.total,memory.used,memory.free,driver_version,name,gpu_serial,display_active,display_mode", "--format=csv,noheader,nounits"], stdout=PIPE)
    output = p.stdout.read().decode('UTF-8')
    # output = output[2:-1] # Remove b' and ' from string added by python
    #print(output)
    ## Parse output
    # Split on line break
    lines = output.split(os.linesep)
    #print(lines)
    numDevices = len(lines)-1
    deviceIds = np.empty(numDevices,dtype=int)
    gpuUtil = np.empty(numDevices,dtype=float)
    memTotal = np.empty(numDevices,dtype=float)
    memUsed = np.empty(numDevices,dtype=float)
    memFree = np.empty(numDevices,dtype=float)
    driver = []
    GPUs = []
    for g in range(numDevices):
        line = lines[g]
        #print(line)
        vals = line.split(', ')
        #print(vals)
        for i in range(10):
            # print(vals[i])
            if (i == 0):
                deviceIds[g] = int(vals[i])
            elif (i == 1):
                gpuUtil[g] = safeFloatCast(vals[i])/100
            elif (i == 2):
                memTotal[g] = safeFloatCast(vals[i])
            elif (i == 3):
                memUsed[g] = safeFloatCast(vals[i])
            elif (i == 4):
                memFree[g] = safeFloatCast(vals[i])
            elif (i == 5):
                driver = vals[i]
            elif (i == 6):
                gpu_name = vals[i]
            elif (i == 7):
                serial = vals[i]
            elif (i == 8):
                display_active = vals[i]
            elif (i == 9):
                display_mode = vals[i]
        GPUs.append(GPU(deviceIds[g], gpuUtil[g], memTotal[g], memUsed[g], memFree[g], driver, gpu_name, serial, display_mode, display_active))
    return GPUs  # (deviceIds, gpuUtil, memUtil)

def get_cpu_usage_in_second():
    with open("/sys/fs/cgroup/cpuacct/cpuacct.usage") as usage:
        cpu_usage_in_nano = usage.readline()
    return float(cpu_usage_in_nano)/1e9 
def get_memory_limit_in_bytes():
    with open("/sys/fs/cgroup/memory/memory.limit_in_bytes") as limit:
        limit_in_bytes = limit.readline()
    return float(limit_in_bytes)

def get_memory_usage_in_bytes():
    with open("/sys/fs/cgroup/memory/memory.usage_in_bytes") as usage:
        usage_in_bytes = usage.readline()
    return float(usage_in_bytes)

def get_memory_usage_percent():
    memory_percent = get_memory_usage_in_bytes()/get_memory_limit_in_bytes()*100
    return memory_percent

def get_cpu_usage_in_second():
    with open("/sys/fs/cgroup/cpuacct/cpuacct.usage") as usage:
        cpu_usage_in_nano = usage.readline()
    return float(cpu_usage_in_nano)/1e9

def get_cpu_system_in_second():
    return time.time()

def get_cpu_load_func():
    previous_cpu_system_in_second = get_cpu_system_in_second()
    previous_cpu_usage_in_second = get_cpu_usage_in_second()
    def get_load():
        curr_cpu_usage_in_second = get_cpu_usage_in_second()
        delta = curr_cpu_usage_in_second - previous_cpu_usage_in_second
        curr_system_usage_in_second = get_cpu_system_in_second()
        delta_system = curr_system_usage_in_second - previous_cpu_system_in_second
        return delta/delta_system*100
    return get_load

get_cpu_load = get_cpu_load_func()

def summary():
    print("memory {0:.2f}%".format(get_memory_usage_percent()))
    print("load {0:.2f}%".format(get_cpu_load()))
    showUtilization()
