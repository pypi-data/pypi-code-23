import subprocess
from Yuki.configDatabase import configdb

def add_config(template=None):
    file_name = configdb.new_config(template)
    try:
        ps = subprocess.Popen("vim {0}", file_name)
        ps.wait()
    except:
        print("Fail to add configuration file")


def add_release(template=None):
    print("Add release file is not supported yet.")
