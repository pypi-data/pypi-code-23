#!/usr/bin/python
# Copyright (c)2012 EMC Corporation
# All Rights Reserved

# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

import json
import common
import urllib

from common import SOSError


class Alerts(object):

    '''
    The class definition for operations on 'Alerts'.
    '''

    # Commonly used URIs
    URI_SERVICES_BASE = ''
    URI_ALERTS = URI_SERVICES_BASE + '/vdc/alerts'

    URI_ALERTS_UNACKED = URI_ALERTS + '/latest'
    URI_ALERTS_ACK = URI_ALERTS + '/{0}/acknowledgement'

    ###################################################
    #
    ###################################################
    def __init__(self, ipAddr, port, output_format = None):
        '''
        Constructor: takes IP address and port of the ECS instance. These are
        needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port
        self.__format = "json"
        if (output_format == 'xml'):
           self.__format = "xml"


    ###################################################
    #
    ###################################################
    def list_unacked(self, args=None):
        xml = False
        if self.__format == "xml":
            xml = True

        uri = Alerts.URI_ALERTS_UNACKED
        qparms = {}
        if args is not None:
            if (args.limit is not None):
                qparms['limit'] = args.limit

        uri += '?' + urllib.urlencode(qparms)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                             uri, None, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s

    ###################################################
    #
    ###################################################
    def ack_alerts(self, alert_id):
        uri = Alerts.URI_ALERTS_ACK.format(alert_id)


        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "PUT",
                                             uri, None)
        return 


    ###################################################
    #
    ###################################################
    def ack_alerts_temp(self, alert_id):
        uri = '/dashboard/alerts'
        body = '/vdc/alerts/' + alert_id  + '/acknowledgment'

        (s, h) = common.service_json_request(self.__ipAddr, '443', "PUT",
                                             uri, body)
        return


    ###################################################
    #
    ###################################################
    def ackall_alerts(self, args):
        result = self.list_unacked()
        alerts = result['alert']
        for alert in alerts:
            alert_id = alert['id']
            if ((args.level is not None) and (alert['severity'] == args.level)):
                self.ack_alerts_temp(alert_id)
            elif args.level is None:
                self.ack_alerts_temp(alert_id)
        return



##########################################################
#
##########################################################
def list_alerts_unacked_parser(subcommand_parsers, common_parser):
    alerts_parser = subcommand_parsers.add_parser(
        'list-unacked',
        description='ECS List unacknowledged alerts',
        parents=[common_parser],
        conflict_handler='resolve',
        help='list unacknowledged alerts')

    alerts_parser.add_argument('-limit', '-l',
                        dest='limit',
                        help='limit the number of unacknowledged alerts returned',
                        required=False)

    alerts_parser.set_defaults(func=list_alerts_unacked)

##########################################################
#
##########################################################
def list_alerts_unacked(args):

    obj = Alerts(args.ip, args.port)
    try:
        return obj.list_unacked(args)
    except SOSError as e:
        raise e


##########################################################
#
##########################################################
def ack_alert_parser(subcommand_parsers, common_parser):
    alerts_parser = subcommand_parsers.add_parser(
        'ack',
        description='acknowledge an alert',
        parents=[common_parser],
        conflict_handler='resolve',
        help='acknowledge an alert')

    alerts_parser.add_argument('-id',
                        dest='id',
                        help='the alert id to be acknkowledged',
                        required=True)

    alerts_parser.set_defaults(func=ack_alerts)

##########################################################
#
##########################################################
def ack_alerts(args):

    obj = Alerts(args.ip, args.port)
    try:
        return obj.ack_alerts(args.id)
    except SOSError as e:
        raise e

#########################################################
#
##########################################################
def ack_alert_temp_parser(subcommand_parsers, common_parser):
    alerts_parser = subcommand_parsers.add_parser(
        'ack',
        description='acknowledge an alert',
        parents=[common_parser],
        conflict_handler='resolve',
        help='acknowledge an alert')

    alerts_parser.add_argument('-id',
                        dest='id',
                        help='the alert id to be acknkowledged',
                        required=True)

    alerts_parser.set_defaults(func=ack_alerts_temp)

##########################################################
#
##########################################################
def ack_alerts_temp(args):

    obj = Alerts(args.ip, args.port)
    try:
        return obj.ack_alerts_temp(args.id)
    except SOSError as e:
        raise e

#########################################################
#
##########################################################
def ackall_alerts_parser(subcommand_parsers, common_parser):
    alerts_parser = subcommand_parsers.add_parser(
        'ackall',
        description='acknowledge all alerts or all alerts of a particular serverity level',
        parents=[common_parser],
        conflict_handler='resolve',
        help='acknowledge an alert')

    alerts_parser.add_argument('-level',
                        dest='level',
                        help='filter the acknowledgement to alerts of this specific level',
                        required=False)

    alerts_parser.set_defaults(func=ackall_alerts)

##########################################################
#
##########################################################
def ackall_alerts(args):

    obj = Alerts(args.ip, args.port)
    try:
        return obj.ackall_alerts(args)
    except SOSError as e:
        raise e




##########################################################
#
##########################################################
def alerts_parser(parent_subparser, common_parser):
    # main tenant parser
    parser = parent_subparser.add_parser(
        'alerts',
        description='to list and acknowledge ECS alerts',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on ECS alerts')
    subcommand_parsers = parser.add_subparsers(help='Use One Of Commands')

    list_alerts_unacked_parser(subcommand_parsers, common_parser)
    #ack_alert_parser(subcommand_parsers, common_parser)
    ack_alert_temp_parser(subcommand_parsers, common_parser)
    ackall_alerts_parser(subcommand_parsers, common_parser)



