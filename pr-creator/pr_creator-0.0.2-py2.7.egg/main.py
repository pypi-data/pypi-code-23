#!/usr/bin/env python

import logging
import argparse
from collections import OrderedDict
import os
from .tickets.jira import *
from .tickets.branches import *
from .tickets.completer import branch_autocomplete
from .tickets import github

DEFAULT_BASE = 'develop'

logger = logging.getLogger(__name__)


def process(app_bases, args):
    logger.info("Starting")
    logger.info("Making a ticket")

    # ticket = make_ticket(args)

    logger.info("Making branches...")
    for app in apps:
        logger.info("Making branch for for {0}".format(app))
        git_exec(app, 'checkout {0}'.format(app_bases[app]))
        git_exec(app, "checkout -b {branch_name}".format(branch_name=args.branch_name))

        if app != 'eab_base':
            logger.info("Changing requirements files")
            change_reqs_files(app, args)
            git_exec(app, 'add $PROJECTS/{app}/requirements'.format(app=app))
            git_exec(app, 'commit -m "Change reqs"')
            logger.info("Committing")

        if args.force_pr:
            cmd = 'touch $PROJECTS/{app}/fakemagicfile.sh'.format(app=app)
            subprocess.call(cmd, shell=True)
            git_exec(app, 'add $PROJECTS/{app}/fakemagicfile.sh'.format(app=app))
            git_exec(app, 'commit -m "Make a fake file"')
            cmd = 'rm $PROJECTS/{app}/fakemagicfile.sh'.format(app=app)
            subprocess.call(cmd, shell=True)
            git_exec(app, 'rm $PROJECTS/{app}/fakemagicfile.sh'.format(app=app))
            git_exec(app, 'commit -m "Delete a fake file"')

    logger.info("Pushing to remote")
    for app in apps:
        git_exec(app, 'push --set-upstream origin {br}'.format(app=app, br=args.branch_name))

    prs = OrderedDict()
    logger.info("Making PRs")
    for app, url in github.pr_urls.iteritems():
        logger.info("Making PRs for {0}".format(app))
        params = {
            'head': args.branch_name,
            'base': app_bases[app],
        }
        prs[app] = github.get_or_create_pull_request(url, params, args)

    messages = [ticket_url(args.ticket_id)]
    messages.extend([x[1]['html_url'] for x in prs.items()])
    message_str = "\n".join(messages)
    logger.info("Composed the message string")
    for app, pr in prs.iteritems():
        logger.info("Updating the message for {0}".format(pr))
        github.update_pr("{0}/{1}".format(github.pr_urls[app], pr['number']), message_str, args)

    # logger.info("Updating the message for the ticket")
    # update_ticket(args)
    logger.info("Done!")
    print([x[1]['html_url'] for x in prs.items()])


def main():
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('--local', '-l', action='store_true')
    parser.add_argument('--ticket_name', '-b', help="Branch name to use without story suffix", required=True)
    parser.add_argument('--ticket-id', '-t', help='Ticket name on JIRA, ex NAV-5050', required=True)
    parser.add_argument('--ticket-type', '-type', help='Type of ticket.  Default feature.', default='feature')
    parser.add_argument('---pick-base-branch', '-pb', action='store_true',
                        help='Interactively choose your base branch, instead of using develop.')
    # parser.add_argument('--exclude', '-x', action='store',
    #                     help='Exclude these apps from operation. Ex `greendale,notification_service`')
    parser.add_argument('--force-pr', '-f', action='store_true',
                        help='Make sure a PR gets made by making a noop commit and reverting it. (Default True)',
                        default=True)
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    args.user = github.get_user()
    args.branch_name = branch_name(args)

    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

    if not GITHUB_TOKEN:
        raise RuntimeError("You need a GITHUB_TOKEN env var with your github token to use this tool.")

    logging.info("Getting app base branches")
    app_bases = {}
    for app in apps:
        if args.pick_base_branch:
            base_branch = branch_autocomplete(app)
            app_bases[app] = base_branch
        else:
            app_bases[app] = DEFAULT_BASE
    process(app_bases, args)
