import subprocess
from Yuki.configDatabase import configdb

def add_config(template=None):
    file_name = configdb.new_config(template)
    print(file_name)
    try:
        #FIXME other editor support
        ps = subprocess.Popen("vim {0}".format(file_name), shell=True)
        ps.wait()
    except:
        print("Fail to add configuration file")


def add_release(template=None):
    print("Add release file is not supported yet.")
