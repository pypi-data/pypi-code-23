# Jobs handling suite

import subprocess
import argparse
from collections import Counter


def main() :
    print "Welcome to AliGEM | Jobs"

def exec_alien_cmd(process = [], verbose=False) :
    """
    Wrapper function to execude terminal commands within python based on subprocess package.
    Example of input process list ['alien_top','-all_status','-user',str(user)]
     - first element is the command
     - following arguments is parameter (& values) sequence
    TODO: ATM it is handled by try-except clause, a Popen might be more suitable (and stable?) solution
    """

    if not process :
        print 'Process list is empty. Nothing to execute!'
        return

    try :
        output = subprocess.check_output(process)
        return { "cmd" : process, "returncode" : 0, "output" : output }

    except subprocess.CalledProcessError as error :
        if(verbose) :
            print("CalledProcessError exception caught!")
            print("Error return code:\n" + str(error.returncode))
            print("Error cmd:\n" + str(error.cmd))
            print("Error output:\n" + str(error.output))

        return { "cmd" : error.cmd, "returncode" : error.returncode, "output" : error.output }

    except OSError as error :
        print "OSError expection caught! Unknown process '" + str(process) + "'"
        if verbose : print error

    except ValueError as error :
        print "ValueError expection caught! Popen (likely) invoked with invalid arguments"
        if verbose : print error

    return { "cmd" : str(process), "returncode": None, "output" : str(error) }

def fetch_jobs(user,verbose=False,debug=False) :
    """
    Returns list of job dicts from Grid query for a single user
    """
    job_string = exec_alien_cmd(['alien_top','-all_status','-user',str(user)],verbose=verbose)['output']

    # stripping useless characters within jobs output
    job_string = job_string.replace(" ","") # removing whitespaces
    job_string = job_string.rstrip("\n\n") # stripping last \n\n to avoid empty entries
    jobs = job_string.split("\n\n")

    list_jobs = []
    for job in jobs :
        processed_job = process_single_job(job)
        if validate_single_job(processed_job,debug=debug) : list_jobs.append(processed_job)
    return list_jobs

def process_single_job(job='') :
    """ Returns a dict with a data from single job"""
    job = job.split("\t")

    if len(job) < 4 :
        return None

    if job[4].startswith("pcapiserv") :
        job_type = 'master'
    else :
        job_type = 'subjob'

    single_job = { 'id':job[0], 'group':job_type, 'status':job[1], 'user':job[2], 'script':job[3], 'server':job[4] }
    return single_job

def validate_single_job(job,debug=False) :
    """ Returns True if job is valid, False otherwise """
    isOK = True

    if job is None :
        if debug : print "invalid job"
        return False

    if not job['id'].isdigit() :
        isOK = False
        if debug : print "job id '%s' not validated" % str(job['id'])

    if ( (job['group'] == 'master') and (not job['server'].startswith('pcapiserv')) ) :
        isOK = False
        if debug : print "job group '%s' not validated" % job['group']

    if (job['group'] == 'subjob') and (not job['server'].startswith('aliendb')) :
        isOK = False
        if debug : print "job group '%s' not validated" % job['group']

    if debug and (isOK == False) : print(job)
    return isOK

def get_status(user='vpacik',debug=False,only_positive=False) :
    """
    Fetching jobs from Grid servers, sorting them according to their status and prints brief overview
    """

    if user == None :
        print 'User not specified. This might take long time. Aborted!'
        return

    # Works well except for states with starts with something; ie. ERROR_*, DONE_*

    jobs = fetch_jobs(str(user),debug=debug)
    if len(jobs) == 0 :
        print "No (validated) jobs found."
        return

    master = [ job['status'] for job in jobs if job['group'] == 'master' ]
    num_master = len(master)
    counts_master = Counter(master)

    sub_jobs = [ job['status'] for job in jobs if job['group'] == 'subjob' ]
    num_subjob = len(sub_jobs)
    counts_subjob = Counter(sub_jobs)

    # getting general counts of finer split elements (such as ERROR_* and DONE_*)
    for key,value in counts_master.iteritems() :
        if key.startswith("ERROR") : counts_master += Counter({'ERROR_ALL' : value})
        if key.startswith("DONE") : counts_master += Counter({'DONE_ALL' : value})

    for key,value in counts_subjob.iteritems() :
        if key.startswith("ERROR") : counts_subjob += Counter({'ERROR_ALL' : value})
        if key.startswith("DONE") : counts_subjob += Counter({'DONE_ALL' : value})

    # lists of job states used for ordered printing (NB: counts.keys() could be used instead, however it will be "randomly" ordered)
    states_master = [ "DONE_ALL", "SPLIT", "INSERTING", "RUNNING", "SAVING", "SAVED", "ERROR_ALL", "ZOMBIE", "REST"]
    states_subjob = [ "DONE_ALL", "WAITING", "ASSIGNED", "STARTED", "RUNNING", "SAVING", "SAVED", "ERROR_ALL", "EXPIRED", "ZOMBIE", "REST"]

    # estimating REST state (one not listed (and thus printed) in above lists)
    num_rest = num_master
    for key, value in counts_master.iteritems() :
        if key in states_master : num_rest -= value
    counts_master.update({'REST' : num_rest})

    num_rest = num_subjob
    for key, value in counts_subjob.iteritems() :
        if key in states_subjob : num_rest -= value
    counts_subjob.update({'REST' : num_rest})

    # Printing status output to the user
    def printStatusLine(label, num, num_all, only_positive=only_positive) :
        perc = -1.0
        if num_all > 0.0 : perc = 100*float(num)/num_all
        if only_positive and num == 0 : return

        print '%10s: %5d %6.1f%%' % (label, num, perc)
        return

    print '######################################'
    print '  Jobs status for user "%s"' % user
    print '======= Masterjobs (%d) ==============' % num_master
    for key in states_master :
        printStatusLine(key, counts_master[key], num_master)

    if not only_positive or (only_positive and num_subjob > 0) :
        print '======= Subjobs (%d) =================' % num_subjob
        for key in states_subjob :
            printStatusLine(key, counts_subjob[key], num_subjob)

    print '######################################'

    if debug :
        print "Master :",; print counts_master
        print "Subjob :",; print counts_subjob
    return

def kill_job_id(job_id, verbose=False) :
    """ Kill a single job based on input id """
    print exec_alien_cmd(['alien_kill',str(job_id)],verbose=verbose)['output']

def kill_jobs(jobs_list,verbose=False,debug=True) :
    """ Kill ALL jobs based on provided list with (filtered) jobs. """
    if not jobs_list :
        print 'List of jobs is empty. Nothing to kill'
        return

    for job in jobs_list :
        job_id = job['id']

        if debug :
            print 'Job ID to kill %s (would be killed, running in debug mode)' % (job_id)
            print job
        else :
            kill_job_id(job_id,verbose=verbose)
    return

def filter_jobs(list_jobs, group=None, status=None, server=None, user=None, verbose=False) :
    """ Returns a list with jobs passing filtering criteria """

    if not list_jobs : # check if list is empty
        if verbose : print 'Input job list is empty. Nothing to filter'
        return []

    filtered_jobs = list_jobs

    if user != None :
        filtered_jobs = [ job for job in filtered_jobs if job['user'] == str(user) ]

    if group != None :
        filtered_jobs = [ job for job in filtered_jobs if job['group'] == str(group) ]

    if server != None :
        filtered_jobs = [ job for job in filtered_jobs if job['server'].startswith(str(server)) ]

    if status != None :
        filtered_jobs = [ job for job in filtered_jobs if job['status'].startswith(str(status)) ]

    return filtered_jobs

def kill_done(user, verbose=False, debug=False) :
    filtered = filter_jobs(fetch_jobs(user), status="DONE", verbose=verbose)
    if verbose : print "Number of jobs to be deleted: %d " % len(filtered)
    kill_jobs(filtered, debug=debug)
    return

def kill_all(user, verbose=False, debug=False) :
    filtered = filter_jobs(fetch_jobs(user),group="master",verbose=verbose)
    if verbose : print "Number of jobs to be deleted: %d " % len(filtered)
    kill_jobs(filtered, debug=debug)
    return

def resubmit(user, verbose=False, debug=False) :

    # define a list with "master" and "subjob" for sequential resubmitting
    groups = ["master","subjob"]

    for group in groups :
        jobs_list = fetch_jobs(user,verbose=verbose,debug=debug)
        jobs_group = filter_jobs(jobs_list,group=group,verbose=verbose)

        filtered = []
        filtered.extend(filter_jobs(jobs_group,status="ERROR",verbose=verbose))
        filtered.extend(filter_jobs(jobs_group,status="EXPIRED",verbose=verbose))
        filtered.extend(filter_jobs(jobs_group,status="ZOMBIE",verbose=verbose))

        if len(filtered) == 0 :
            print "No %s jobs to resubmit!" % str(group)
            return

        for job in filtered :
            job_id = job['id']

            if debug :
                print job_id
            else :
                print exec_alien_cmd(['alien_resubmit',str(job_id)],verbose=verbose)['output']

    return

# ==============================================================================
