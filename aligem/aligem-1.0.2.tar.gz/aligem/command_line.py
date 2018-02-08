import jobs,token
import argparse
import subprocess

def main() :
    ### top-level group (L0)
    parser = argparse.ArgumentParser(description="Welcome to AliGEM - ALICE Grid Enviroment Manager (https://github.com/vpacik/aligem)")
    parser.add_argument("-v","--verbose", help="produce verbose output", action="store_true")
    parser.add_argument("-d","--debug", help="debugging mode (additional printout)", action="store_true")
    parser.add_argument("--version", action="version", version='0.1', help="print current version")
    subparsers = parser.add_subparsers(title="operations",dest="command",)

    ### sub-parsers
    # jobs parser (L1)
    parser_jobs = subparsers.add_parser("jobs", help="Grid jobs operations")
    jobs_subparsers = parser_jobs.add_subparsers(dest="job_command")

    # jobs sub-parsers (L2)
    jobs_subparser_status = jobs_subparsers.add_parser("status", help = "print overview of currently registered grid jobs")
    jobs_subparser_status.add_argument("-o","--offline", help="running in OFFLINE mode for testing purposes", action="store_true", default=False)
    jobs_subparser_status.add_argument("--only-positive", help="print only states with at least 1 (sub)job", action="store_true", default=False)
    jobs_subparser_status.add_argument("-u","--user", help="specify USER as CERN username")

    jobs_subparser_kill = jobs_subparsers.add_parser("kill", help = "kill grid job(s) in DONE state")
    jobs_subparser_kill.add_argument("-A","--all", help="kill ALL registered jobs (independent of state)", action="store_true",dest="kill_all")
    # jobs_subparser_kill.add_argument("-u","--user", help="specify USER as CERN username")

    jobs_subparser_resubmit = jobs_subparsers.add_parser("resub", help = "re-submit all grid job(s) in ERROR, EXPIRED or ZOMBIE state")

    # token parser (L1)
    parser_token = subparsers.add_parser("token", help="AliEn token operations")
    token_subparsers = parser_token.add_subparsers(dest="token_command")
    token_subparser_init = token_subparsers.add_parser("init", help="Initialize new token")
    token_subparser_destroy = token_subparsers.add_parser("destroy", help="Destoy current token")
    token_subparser_info = token_subparsers.add_parser("info", help="List token information")


    args = parser.parse_args()
    args = vars(args)

    debug = args['debug']
    verbose = args['verbose']

    if debug :
        print "=== Arguments ================================="
        print args
        print "==============================================="

    if args['command'] == 'jobs' :
        if debug : print "inside jobs"

        # check for valid token (if not found, token-init)
        if (token.check() == False) and ("offline" in args) and (args['offline'] == False) :
            print "No valid token found. Initializiting new token!"
            token.init()

        if "user" in args and args['user'] is not None :
            local_user = args['user']
        else :
            if "offline" in args :
                local_user = subprocess.check_output("whoami").strip()
            else :
                local_user = jobs.exec_alien_cmd("alien_whoami")['output'].strip()

        if args['job_command'] == 'status' :
            if debug : print "inside status"
            offline = args['offline']
            only_positive = args['only_positive']

            jobs.get_status(local_user,offline=offline, debug=debug, only_positive=only_positive)

        if args['job_command'] == 'kill' :
            if debug : print "inside kill"
            # user = args.user

            if args['kill_all'] :
                if debug : print "kill all is ON!"
                jobs.kill_all(local_user, debug = debug)
            else :
                jobs.kill_done(local_user,debug=debug)


        if args['job_command'] == 'resub' :
            if debug : print "inside resubmit"
            # user = args.user
            jobs.resubmit(local_user,debug=debug)


    if args['command'] == 'token' :
        # token.info()
        if args['token_command'] == "init" :
            if not token.check() :
                token.init()
            else :
                print "Valid token already exists! Destroy it first!"

        if args['token_command'] == "destroy" :
            token.destroy()

        if args['token_command'] == "info" :
            token.info()

        # print "token command not implemented (yet)"


    return
