#-*-coding:iso-8859-1-*-
#!/logiciels/public/bin/python-2.4
#
#

"""
module finding the environment in where maestro is called
"""

import socket
import os


SCHEDULER = {
             "shaheen":("slurm",32," -l nodes=1:ppn=1,walltime=12:00:00"),
             "localhost":("unix",10,"")}
TMPDIR = "/tmp"
PYTHON_EXE = "python"

if os.name == "nt":
    PYTHON_EXE = "e:/python25/python.exe"


CORE_PER_NODE_REGARDING_QUEUE={}
DEFAULT_QUEUE="default"
 
 
def get_machine():
    global CORE_PER_NODE_REGARDING_QUEUE, DEFAULT_QUEUE
    """
    determines the machine maestro is running on and sets
    proper local variable (name of the machine and path
    to the local working directory
    """
    
    tmp_directory = "/tmp"
    machine = socket.gethostname()
    if (str.find(machine,"stampede")>-1):
        machine = "stampedepp"
        tmp_directory = os.getenv("SCRATCH")
        CORE_PER_NODE_REGARDING_QUEUE["development"] = 16
        CORE_PER_NODE_REGARDING_QUEUE["largemem"] = 32
        DEFAULT_QUEUE="normal"
    elif (machine[:3]=="cdl" or machine[:3]=="nid"):
        machine = "shaheen"
        tmp_directory = "/scratch/tmp"
        CORE_PER_NODE_REGARDING_QUEUE["workq"] = 32
        DEFAULT_QUEUE="workq"
    else:
        machine = "localhost"
        tmp_directory = "/tmp"
    return machine, tmp_directory



MY_MACHINE, TMPDIR = get_machine()
MY_MACHINE_FULL_NAME = socket.gethostname()

