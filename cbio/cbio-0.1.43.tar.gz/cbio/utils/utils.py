import os
import subprocess
import sys
import logging
import coloredlogs



def check_input(starting_files):
    """
    Function that checks if a list of input files exists or not

    Parameters
    ----------
    starting_files : list
        List of paths that are going to be evaluated for existance

    Returns
    -------
    None

    """

    # Instance must be a list of files to check
    if not isinstance(starting_files, list):
        raise TypeError("starting_files must be a list of files")

    for in_file in starting_files:
        # Check if file is a path or string
        if not isinstance(in_file, str):
            raise TypeError("file must be a string (" + str(in_file) + ")")

        if not os.path.exists(in_file):
            raise Exception('Input file does not exists -> ' + in_file)

    return None


def check_already_exist(input_path):
    """
    Check if file already exists or not to avoid overwritting it

    Parameters
    ----------
    input_path : str
        Path to the file that is going to be checked

    Returns
    -------
    None

    """
    # TODO: Change this to a list of files
    if not isinstance(input_path, str):
        raise TypeError("Argument given to check format must be a string, it was " + str(type(input_path)))
    input_path = os.path.abspath(input_path)
    if os.path.exists(input_path):
        raise Exception('File "' + input_path + '" already exists, cannot overwrite it')


def check_empty(element_list):
    if len(element_list) == 0:
        raise IndexError("List of files to check format is empty")

    return None


def create_folders(dir_list):
    """
    Create all folders from a list passed by arguments if they do not exist

    Parameters
    ----------
    dir_list : list
        List containing all directories that are going to be created
    """
    # Check if input file_list is indeed a list of strings
    if not isinstance(dir_list, list):
        raise TypeError("Argument given to check format must be a list of string")

    # Check if list if empty. In that case, raise exception
    check_empty(dir_list)

    for folder in dir_list:

        if not isinstance(folder, str):
            raise TypeError("Argument given to check format must be a string, it was " + str(type(file_name)))

        if not os.path.exists(folder):
            cmd = 'mkdir ' + folder
            print('#[LOG]: Created folder -> ' + folder)
            run_cmd(cmd, 1)


def joinPath(pathItems):
    path = os.path.join(*pathItems)
    return os.path.normpath(path)


def sanitisePath(path):
    """ normalize and remove trailing slashes in paths"""
    return os.path.normpath(path)


def run_cmd(cmd, output=0):
    """
    Function that runs a command given by user
    """

    if output == 0:
        process = subprocess.Popen(cmd, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = process.stdout.readline()
        out = out.decode("utf-8").strip('\n')

        while out != '':
            print(out)
            out = process.stdout.readline()
            out = out.decode("utf-8").strip('\n')

    if output == 1:
        process = subprocess.Popen(cmd, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = []
        out = process.stdout.readline()
        out = out.decode("utf-8").strip('\n')

        while out != '':
            output.append(out)
            out = process.stdout.readline()
            out = out.decode("utf-8").strip('\n')

        return output

    else :
        try:
            os.system(cmd)
        except :
            raise Exception("Command failed: " + cmd + "\n")


def check_format(file_list, suffix):
    """
    Check if all the files in a list passed by arguments fill the requirement
    of a specified suffix.

    Parameters
    ----------
    file_list : list
        List of paths (str) containing all files to check its format
    suffix : str
        String that contains the suffix that all files passed in the previous
        argument must have
    """

    # Check if input file_list is indeed a list of strings
    if not isinstance(file_list, list):
        raise TypeError("Argument given to check format must be a list of string")

    # Check if list if empty. In that case, raise exception
    check_empty(file_list)

    # Check if suffix is string
    if not isinstance(suffix, tuple):
        raise TypeError("Suffix must be a tuple (tuples of 1 must be \"(str,)\", don't forget the semicolon), it was " + str(type(suffix)))

    # For each file, see if file is a string and if suffix is the one that must be
    for file_name in file_list:
        if not isinstance(file_name, str):
            raise TypeError("Argument given to check format must be a string, it was " + str(type(file_name)))

        if file_name.endswith(suffix):
            return(None)
        else:
            raise NameError("Suffix of the file must be in " + str(suffix))


def setLogger(mode, module):
    """Define the log that we will use."""

    # create logger with 'spam_application'
    logger = logging.getLogger(module)
    logger.setLevel(logging.DEBUG)

    log = logging.StreamHandler()

    # Select the mode
    if mode is 'Debug':
        log.setLevel(level=logging.DEBUG)
    elif mode is 'Production':
        log.setLevel(level=logging.INFO)

    formatter = logging.Formatter('#[%(levelname)s] - %(name)s - %(message)s')
    log.setFormatter(formatter)

    # logger.addHandler(log)

    # read database here
    logger.info("Entering " + mode + " mode")

    return logger


def setMode(args):
    if args.d is True:
        mode = 'Debug'
    else:
        mode = 'Production'

    return mode


def set_log(name, dirs):

    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    for d in dirs:

        # create a file handler
        handler = logging.FileHandler(d)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        log.addHandler(handler)

    # Create stream handler
    coloredlogs.install(level='INFO', logger=log)
    # ch = logging.StreamHandler(sys.stdout)
    # ch.setLevel(logging.INFO)
    # ch.setFormatter(formatter)
    #
    # log.addHandler(ch)

    return log
