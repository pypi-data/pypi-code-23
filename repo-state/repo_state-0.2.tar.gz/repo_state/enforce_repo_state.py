"""
Command-line utility to enforce a given repository state onto the given directory
"""

import os
import sys
import json
from argparse import ArgumentParser
from state import enforce_state, \
    GitRepoNotClean, GitCommitNotAvailable, GitRemotesAmbiguous, EnforceStateError


def desc():
    return __doc__


def main():
    parser = ArgumentParser(description=desc())
    parser.add_argument('state_file', help='path to state file')
    parser.add_argument('--path', help="path to directory to enforce repo state")
    args = parser.parse_args()

    try:
        f = open(args.state_file)
    except (IOError, OSError) as e:
        print "\nERROR: " + e.message + "\n"
        sys.exit(1)

    state = json.load(f)
    f.close()

    if args.path:
        path = os.path.abspath(args.path)
    else:
        path = state.get('base_directory')

    try:
        enforce_state(path, state=state)
    except (GitRepoNotClean, GitCommitNotAvailable, GitRemotesAmbiguous, EnforceStateError) as e:
        print e.message
        sys.exit(1)

    print "\nSuccess!\n"

if __name__ == "__main__":
    main()
