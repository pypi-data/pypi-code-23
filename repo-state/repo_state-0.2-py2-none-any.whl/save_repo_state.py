"""
Command-line utility to save the current repository state under a given directory to a JSON file.
"""

import sys
import json
from argparse import ArgumentParser
from state import capture_state, split_with_bash_space_escapes, \
    EnforceStateError, GitRemotesAmbiguous, GitRepoNotClean, GitCommitNotAvailable


def desc():
    return __doc__


def main():
    parser = ArgumentParser(description=desc())
    parser.add_argument('path', help="path to directory to save state for")
    parser.add_argument('-v', '--version', required=True, help='save state with this version number')
    parser.add_argument('-d', '--description', help='save state with this description')
    parser.add_argument('-f', '--file', help='name of file to save state. Default prints to stdout')
    parser.add_argument('--maxdepth', type=int, default=5,
                        help='Max number of levels below the target path to search. Default=5')
    parser.add_argument('--ignore', type=str,
                        help='Quoted, space-separated list of directory names to ignore')
    parser.add_argument('--select', type=str,
                        help='Quoted, space-separated list of subdirectories to explore under the given path')
    args = parser.parse_args()

    ignore_list = None
    if args.ignore:
        ignore_list = split_with_bash_space_escapes(args.ignore)

    select_list = None
    if args.select:
        select_list = split_with_bash_space_escapes(args.select)

    try:
        state = capture_state(args.path,
                              version=args.version,
                              description=args.description,
                              ignore=ignore_list,
                              select=select_list)
    except (EnforceStateError, GitRemotesAmbiguous, GitRepoNotClean, GitCommitNotAvailable) as e:
        print e.message
        sys.exit(1)

    json_state = json.dumps(state, indent=2)

    if args.file is not None:
        with open(args.file, 'w') as f:
            f.write(json_state)
    else:
        print json_state


if __name__ == "__main__":
    main()
