#!/usr/bin/env python3
import os
import sys
import typing
import argparse
from gfb import configuration, git


def startup_error(e: configuration.ConfigError,
                  prompt='Configuration file is missing or corrupt.'):
    if e:
        print(e.message)
    config_path = os.path.expanduser('~/.gfbrc')
    helper = configuration.SetupHelper(config_path)
    do_setup = helper.should_create_configuration(prompt)
    if not do_setup:
        return
    config = helper.setup_walkthrough()
    prompt = 'Would you like to test your configuration? '
    response = helper.read_user_response(prompt)
    if response == 'y':
        test_ok = helper.check_configuration(config)
        if not test_ok:
            print("Invalid credentials - configuration not saved.")
            sys.exit(0)
        else:
            print("Yay, it worked!")
    config.save(config_path)


def find_branches(config: configuration.Config, repo: str, regex: str):
    using_local_repo = (repo is None)
    if not repo:
        cwd = os.getcwd()
        lrf = git.LocalRepoFinder(cwd)
        try:
            repo = lrf.local_repo_name()
        except git.GitError as git_error:
            print("""Unable to locate a repository. Maybe specify a repo name
                  with the '--repo' argument?""")
            sys.exit(1)

    creds = git.Credentials(repo, config.username, config.password,
                            config.api_key)

    rbf = git.BranchFinder(creds)
    try:
        matches = rbf.find_branch(regex)
    except git.GitError as git_error:
        print("{0}".format(git_error.message))
        sys.exit(1)

    selector = git.BranchSelector(matches, using_local_repo)
    branch = selector.choose_branch()
    if branch is None:
        sys.exit(0)

    selector.checkout_branch(branch)


def run_setup_if_requested(argv):
    """ run setup if user requested """
    if len(argv) == 2:
        if argv[1] == '--setup':
            startup_error(None, 'Creating a new configuration file.')
            sys.exit(0)
        if argv[1] == '--version':
            print("0.9b4")
            sys.exit(0)

def setup_argparse() -> argparse.ArgumentParser:
    """ configure and return our argparser """
    args = argparse.ArgumentParser(prog='gfb', allow_abbrev=True)
    args.add_argument('--repo',
                      help='name of github repository to search',
                      dest='repo')
    args.add_argument('--config', help='gfb configuration file',
                      dest='config_file')
    args.add_argument('--setup',
                      help='create a new default configuration file',
                      action='store_true')
    args.add_argument('regex', help='branch regular expression')
    args.add_argument('--version',
                      help='display the current version and exit')

    return args


def main():
    """ application entry point """
    run_setup_if_requested(sys.argv)
    arg_parser = setup_argparse()
    args = arg_parser.parse_args()
    config = configuration.Config()
    config_file = args.config_file if args.config_file else '~/.gfbrc'
    config_path = os.path.expanduser(config_file)
    try:
        config.read_configuration(config_path)
    except (configuration.MissingConfigError,
            configuration.InvalidConfigError) as e:
        startup_error(e)
        sys.exit(0)
    except configuration.BadConfigPermsError as e:
        print(e.message)
        sys.exit(1)

    find_branches(config, args.repo, args.regex)


if __name__ == '__main__':
    main()
