import re
import argparse

REPONAME_REGEX = re.compile(r'([a-zA-Z]+)/([a-zA-Z]+)')

def check_reponame(repo):
    if not REPONAME_REGEX.match(repo):
        raise argparse.ArgumentTypeError(
            "repo must be in the form <username>/<repository>"
        )

    return repo


def create_parser():
    parser = argparse.ArgumentParser(
        description="cloneme: a git clone wrapper to make cloning repos easier"
    )
    parser.add_argument('repo', type=check_reponame)

    return parser
