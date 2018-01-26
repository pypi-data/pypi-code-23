from subprocess import Popen, PIPE
import re
from cStringIO import StringIO
import sys
import time


def get_valid_package_line_list(line_list):
    tmp_line_list = list(line_list)
    for line in tmp_line_list:
        if(line[:2] != "ii"):
            line_list.remove(line)
    return line_list

def get_package_name_ver_dict(line_list):
    package_dict = {}
    for line in line_list:
        line_list = re.split(" +", line)
        package_dict[line_list[1]] = line_list[2]
    return package_dict


def get_system_packages():
    p = Popen(['dpkg', '-l'], stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
    line_list = output.split('\n')
    line_list = get_valid_package_line_list(line_list)
    sys_package_dict = get_package_name_ver_dict(line_list)
    return sys_package_dict




#get_system_packages()