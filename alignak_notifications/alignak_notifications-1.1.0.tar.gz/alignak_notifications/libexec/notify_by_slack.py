#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2018: Alignak contrib team, see AUTHORS.txt file for contributors
#
# This file is part of Alignak contrib projet.
#
# AlignakBackend is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# AlignakBackend is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with AlignakBackend.  If not, see <http://www.gnu.org/licenses/>.
"""
This file is used to send an Alignak notification by posting to a Slack channel
"""

import os
import time
import json
import argparse

from slackclient import SlackClient


def main():
    """
    Main function used to create and send Slack notification

    :return: None
    """
    # Parse command line arguments
    args = parse_args()

    if not args.slack_token:
        args.slack_token = os.environ.get("ALIGNAK_SLACK_API_TOKEN", None)
    if not args.slack_token:
        print("Slack API token is not provided. Unable to post notifications.")
        return 3

    sc = SlackClient(args.slack_token)

    attachments = [
        {
            "fallback": generate_text(args),
            "color": get_state_color(args.state),
            # "pretext": subject(args),
            "author_name": args.author_name,
            "author_link": args.author_url,
            "author_icon": args.author_logo,
            "title": subject(args),
            # "title_link": "https://api.slack.com/",
            "text": generate_markdown(args),
            "footer": "Alignak notification",
            "footer_icon": args.urllogo,
            "ts": args.datebegin
        }
    ]

    print(args)
    res = sc.api_call(
        "chat.postMessage",
        channel="#%s" % (args.To),
        icon_emoji=':-1:',
        as_user=True if args.From else False,
        username=args.From,
        attachments=json.dumps(attachments)
    )
    exit_code = 0
    if not res["ok"]:
        exit_code = 2
        print("Slack notification error: %s" % res["error"])
    else:
        print("Slack message: %s" % res["message"])
    return exit_code

def parse_args():
    """
    Parse the arguments

    :return:
    """
    parser = argparse.ArgumentParser()

    # General arguments
    parser.add_argument('-fr', '--from', dest="From",
                        help="Name of the author. Leave empty to post as a channel bot (default)")
    parser.add_argument('-to', '--to', dest="To", required=True,
                        help="Destination channel")

    parser.add_argument('-pr', '--prefix', dest="prefix", default='',
                        help="Define a prefix for the notification title")

    parser.add_argument('-an', '--author_name', dest="author_name",
                        help="Message author. Set this if you want to have an author "
                             "information on top of the message")
    parser.add_argument('-al', '--author_logo', dest="author_logo",
                        default='https://raw.githubusercontent.com/Alignak-monitoring-contrib/'
                                'alignak-notifications/master/alignak_16x16.png',
                        help="URL of the author icon (used only if author name is set)")
    parser.add_argument('-au', '--author_url', dest="author_url",
                        help="URL of the message author Web site (used only if author name is set)")

    parser.add_argument('-u', '--urllogo', dest="urllogo",
                        default='https://raw.githubusercontent.com/Alignak-monitoring-contrib/'
                                'alignak-notifications/master/alignak_16x16.png',
                        help="URL of the author icon")

    # Slack parameters
    parser.add_argument('-S', '--slack_token', dest="slack_token",
                        help='Define Slack API token')

    # Alignak / monitoring information
    parser.add_argument('-t', '--type', dest="type", required=True,
                        choices=['host', 'service'], help="Type of object")
    parser.add_argument('-nt', '--notificationtype', dest="notificationtype", required=True,
                        help="Type of the notification")
    parser.add_argument('-nc', '--notificationcount', dest="notificationcount", type=int,
                        help="Notification count")
    parser.add_argument('-hn', '--hostname', dest="hostname", required=True,
                        help="Name of the concerned host")
    parser.add_argument('-sn', '--servicename', dest="servicename",
                        help="Name of the concerned service")
    parser.add_argument('-ha', '--hostaddress', dest="hostaddress",
                        default='n/a', help="Address (IP) of the host")
    parser.add_argument('-s', '--state', dest="state", required=True,
                        help="State of the host / service")
    parser.add_argument('-ls', '--laststate', dest="laststate", required=True,
                        help="Last state of the host / service")
    parser.add_argument('-o', '--output', dest="output", required=True,
                        help="Output of the check plugin")
    parser.add_argument('-dt', '--durationtime', dest="durationtime", type=int, default=0,
                        help="Duration of the provided state in seconds")
    parser.add_argument('-db', '--datebegin', dest="datebegin", type=float, required=True,
                        help="Date + time of the beginning of the current state")
    parser.add_argument('-p', '--perfdata', dest="perfdata",
                        help="Performance data string returned by the check plugin")
    parser.add_argument('-i', '--impact', dest="impact",
                        help="Impact")
    parser.add_argument('-w', '--webui_url', dest="webui_url",
                        help="URL of the host/service in the Web User Interface")
    return parser.parse_args()


def subject(args):
    """
    Create the subject of the notification

    :param args:
    :type args:
    :return: subject of the notification
    :rtype: str
    """
    title = []
    if args.type == 'host':
        title.append('%s - Host %s is %s' % (args.notificationtype, args.hostname, args.state))
    elif args.type == 'service':
        title.append('%s - Host %s , service %s is %s' % (args.notificationtype, args.hostname,
                                                          args.servicename, args.state))
    if args.durationtime:
        title.append(' since %s' % (time.strftime("%Hh%Mm%Ss", time.gmtime(args.durationtime))))

    if args.notificationcount and args.notificationcount > 1:
        title.append(', notification #%s' % (args.notificationcount))

    return args.prefix + ' ' + ''.join(title)


def get_state_color(state):
    """
    Get right color for the state

    :param state: the state
    :type state: str
    :return: the color related of the state
    :rtype: str
    """
    # default state color => OK / UP
    state_color = '#27ae60'
    state = state.upper()
    if state == 'WARNING':
        state_color = '#e67e22'
    if state in ['CRITICAL', 'DOWN']:
        state_color = '#e74c3c'
    if state == 'UNKNOWN':
        state_color = '#2980b9'
    if state == 'UNREACHABLE':
        state_color = '#9b59b6'
    if state == 'ACKNOWLEDGE':
        state_color = '#f39c12'
    if state == 'DOWNTIME':
        state_color = '#f1c40f'
    return state_color


def generate_text(args):
    """
    Create the TEXT message for the notification

    :param args:
    :type args:
    :return: the message in plain text format
    :rtype: str
    """
    text_content = []

    text_content.append("Notification: %s" % args.notificationtype)
    if args.type == 'service':
        text_content.append('Host: %s, service: %s is %s'
                            % (args.hostname, args.servicename, args.state))
    else:
        text_content.append('Host: %s is %s'
                            % (args.hostname, args.state))
    text_content.append("-----")
    text_content.append("")
    text_content.append('Check output: %s' % args.output)
    if args.perfdata:
        text_content.append('Performance data: %s' % args.perfdata)
    if args.impact:
        impact = ''
        for _ in range(int(args.impact)):
            impact += '★'
        text_content.append('Business impact: %s' % impact)

    text_content.append('Since date: %s' % time.strftime("%a %d %b %H:%M:%S", time.gmtime(args.datebegin)))
    text_content.append('Since: %s' % time.strftime("%Hh%Mm%Ss", time.gmtime(args.durationtime)))

    if args.webui_url:
        text_content.append('To view more information: %s' % args.webui_url)

    # Create a unique message string
    return '\r\n'.join(text_content)


def generate_markdown(args):
    """
    Create the markdown message for the notification

    :param args:
    :type args:
    :return: the message in markdown format
    :rtype: str
    """
    text_content = []

    # if args.type == 'service':
    #     text_content.append('Host: %s, service: %s is *%s*'
    #                         % (args.hostname, args.servicename, args.state))
    # else:
    #     text_content.append('Host: %s is *%s*'
    #                         % (args.hostname, args.state))
    text_content.append("> Check output: %s" % args.output)
    if args.perfdata:
        text_content.append("> Performance data: %s" % args.perfdata)
    if args.impact:
        impact = ''
        for _ in range(int(args.impact)):
            impact += ':star:'
        text_content.append("> Business impact: %s" % impact)

    text_content.append('Since date: %s' % time.strftime("%a %d %b %H:%M:%S", time.gmtime(args.datebegin)))
    text_content.append('Since: %s' % time.strftime("%Hh%Mm%Ss", time.gmtime(args.durationtime)))
    text_content.append("")

    if args.webui_url:
        text_content.append('To view more information: %s' % args.webui_url)
        text_content.append("")

    # Create a unique message string
    return '\r\n'.join(text_content)


if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)
