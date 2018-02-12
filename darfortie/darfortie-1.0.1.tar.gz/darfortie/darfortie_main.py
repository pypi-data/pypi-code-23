# Script Name: darfortie.py
# Author: Ken Galle
# License: GPLv3
# Description: Adds functionality to the dar utility and in the process makes it
#    simpler to use, although to do this it does make some assumptions and hides
#    some functionality (which comes from the enormous list of dar switches).
#    Note however that a configuration file can be passed thru to dar.  See the
#    dar man page for details on its structure ("CONDITIONAL SYNTAX").
#    It manages the creation of incremental backups based on the most recent
#    available dar file with the same base name in a given directory.
#    It provides a way to specify a configuration file for dar without worrying
#    about the current environment (/etc/darrc, ~/.darrc).
#    It also allows you to pass thru dar prune paths.

# Note on destination naming convensions:  TODO

#    Return values:
#     1xx, where xx is any error value returned from dar during archive creation.
#     2yy, where yy is any error value returned from dar during archive testing.
#       dar return values range from 1 to 11 (see dar man page, "EXIT CODES")
#     Returns 0 on success (both create and test succeeded).
#
# TODO: attempt to uncover additional exceptions that are not handled and assign
#  error codes to these.

# TODO: test for existance of dar and if not found exit with error code.
#  Currently the subprocess fails and returns with error code of 1.

# TODO: add support for restoring a batch of archives

# TODO: packaging: http://blog.ablepear.com/2012/10/bundling-python-files-into-stand-alone.html

# TODO: Make sure dar catalog files also work as previous backup reference;
# dar has no convension for the name created (it has to be specified with -c), so we create the convension -
# "destination/asus_root_system_daily_20131227_0347UTC_catalog.1.dar"

# TODO: add option to specify path to create a catalog file of the just created archive in; defaults
# to the dest_path.

# TODO: allow the -i switch to be used for the first backup intead of erroring out.


import subprocess
import logging
import glob
import os
from darfortie import darfortie_params
import datetime
from darfortie import darfortie_previous_file

def add_dar_path_to_process_strings(params, process_strings):
    if params['dar_path'] is not None:
        process_strings.append(params['dar_path'])
    else:
        process_strings.append('dar')

def main():
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger('darfortie')
    
    # params to directly use in the call to dar
    params = {}
    
    # get params
    params = darfortie_params.parse()
    
    # build up a list of strings to send into the subprocess
    process_strings = []
    
    add_dar_path_to_process_strings(params, process_strings)
    
    # source (root) path
    process_strings.append('-R')
    process_strings.append(params['source_path'])
    
    # get the current date/time in a string usage as a suffix to the filename
    date_now = datetime.datetime.utcnow()
    date_string = date_now.strftime("%Y%m%dT%H%M") + "UTC"
    log.info("date_string=" + date_string)
    
    # create the destination basename (includes path, if any)
    destination_basename = params['dest_path_and_base_name'] + "_" + date_string
    log.info("destination_basename=" + destination_basename)
    
    # incremental
    if params['incremental']:
        dest_basename = os.path.basename(params['dest_path_and_base_name'])
        # if user specified a different path for the previous file, swap out the paths
        if params['previous_path'] is not None:
            # get base name without path and combine with the new path
            path_and_basename_to_search = os.path.join(params['previous_path'], dest_basename)
        else:
            path_and_basename_to_search = params['dest_path_and_base_name']
        
        log.info("path_and_basename_to_search=" + path_and_basename_to_search)
        # get list of files and dates, sort and take newest one
        # strip off .xx.dar
        full_previous_file = darfortie_previous_file.get_previous_file(path_and_basename_to_search)
        log.info("full_previous_file=" + str(full_previous_file))
        if full_previous_file is not None:
            previous_file = darfortie_previous_file.remove_slice_number_and_extension(full_previous_file)
            log.info("previous_file=" + previous_file)
            if previous_file is not None:
                process_strings.append('-A')
                process_strings.append(previous_file)
    
                # add previous date/time to current filename
                previous_datetime = darfortie_previous_file.get_previous_file_date_time(dest_basename, previous_file)
                destination_basename = destination_basename + "_based_on_" + previous_datetime
            else:
                log.error("Unable to find previous file for incremental backup")
                exit(3)
        else:
            log.error("Unable to find previous file for incremental backup")
            exit(3)
    
    # archive to create
    process_strings.append('-c')
    process_strings.append(destination_basename)
    
    # define config parameter string
    # because of conditionals within config file (e.g. 'create:') this has to come after dar -c option.
    if params['config'] is not None:
        process_strings.append('--noconf')
        process_strings.append('--batch')
        process_strings.append(params['config'])
    
    # define prune paramter string
    if params['prune'] is not None:
        for onePath in params['prune']:
            process_strings.append('-P')
            process_strings.append(onePath)
    
    # exclude the destination archive(s) in case they are being created somewhere in the source directory path
    destination_name_without_path = os.path.basename(destination_basename);
    process_strings.append('-X')
    process_strings.append(destination_name_without_path + '*.*.dar');
    
    # log values from process_strings
    i = 1
    for process_string in process_strings:
        log.info(str(i) + ' : ' + process_string)
    del(i)
    
    # make call to dar
    return_code = subprocess.call(process_strings, shell=False)
    if return_code > 0:
        return_code = return_code + 100
    
    # log return value
    log.info('dar create archive return value=' + str(return_code))
    
    # if not error, then continue on to test
    if return_code == 0:
        test_process_strings = []
        add_dar_path_to_process_strings(params, test_process_strings)
        # test archive just created
        test_process_strings.append('-t')
        test_process_strings.append(destination_basename)
        # make call to dar
        test_return_code = subprocess.call(test_process_strings, shell=False)
        # log return value
        log.info('dar test archive return value=' + str(test_return_code))
        if test_return_code > 0:
            return_code = test_return_code + 200
    exit(return_code)

if __name__ == '__main__':
    main()
