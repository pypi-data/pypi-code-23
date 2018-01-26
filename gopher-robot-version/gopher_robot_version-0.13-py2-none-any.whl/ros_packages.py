import os
from os.path import isfile
import xml.etree.ElementTree as ET

def list_files(startpath):
    file_list = []
    dir_list = []
    content = os.listdir(startpath)
    for element in content:
        if (isfile(startpath + "/" + element) == True):
            file_list.append(startpath + "/" + element)
        else:
            dir_list.append(startpath + "/" + element)

    #print dir_list
    for paths in dir_list:
        file_list += list_files(paths)

    return file_list


def get_packages(file_list):
    tmp_list = list(file_list)
    for file in tmp_list:
        fname = file.split("/")
        if(fname[-1] != "package.xml"):
            file_list.remove(file)
    return file_list

def get_package_list(root_path):
    flist = list_files(root_path)
    flist = get_packages(flist)
    return flist


def get_ros_packages(root_path):
    version_dict = {}
    path_list = get_package_list(root_path)
    for path in path_list:
        tree = ET.parse(path)
        root = tree.getroot()
        for element in root.findall('name'):
            name = element.text
        for element in root.findall('version'):
            version = element.text
        version_dict[name] = version
    return version_dict


#print get_ros_packages("/opt/yujin/amd64/indigo-devel")