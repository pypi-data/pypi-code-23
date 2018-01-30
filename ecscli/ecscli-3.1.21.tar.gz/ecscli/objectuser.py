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
import config
import urllib

from common import SOSError


class Objectuser(object):

    '''
    The class definition for operations on 'Objectuser'.
    '''

    # Commonly used URIs for the 'objectuser' module

    URI_SERVICES_BASE = ''
    URI_WEBSTORAGE_USER = URI_SERVICES_BASE + '/object/users'
    URI_WEBSTORAGE_USER_DEACTIVATE = URI_WEBSTORAGE_USER + '/deactivate'
    URI_WEBSTORAGE_USER_INFO = URI_WEBSTORAGE_USER + '/{0}/info'
    URI_WEBSTORAGE_USER_NS_INFO = URI_WEBSTORAGE_USER + '/{0}'
    URI_WEBSTORAGE_USER_LOCK = URI_WEBSTORAGE_USER + '/lock'
    URI_WEBSTORAGE_USER_LOCK_INSTANCE = URI_WEBSTORAGE_USER_LOCK + '/{0}'
    URI_WEBSTORAGE_USER_SET_TAG = URI_WEBSTORAGE_USER + '/{0}/tags'
    URI_WEBSTORAGE_USER_QUERY = URI_WEBSTORAGE_USER + '/query'


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


    def objectuser_list(self, uid=None, namespace=None):
        '''
        Gets details for the specified user identifier and namespace.

        If no user identifier is provided, gets all identifiers for
        the given namespace.

        If neither user identifier nor namespace is provided, gets
        identifiers for all configured users.
        '''

        # info on single user
        if (uid is not None and namespace is not None):
            uri = Objectuser.URI_WEBSTORAGE_USER_INFO.format(uid) \
                  + "?namespace=" + namespace


        # info on all users in namespace
        elif (uid is not None and namespace is None):
            uri = Objectuser.URI_WEBSTORAGE_USER_INFO.format(uid)


        # info on all users in namespace
        elif (uid is None and namespace is not None):
            uri = Objectuser.URI_WEBSTORAGE_USER_NS_INFO.format(namespace)

        # info on all users
        else:
            uri = Objectuser.URI_WEBSTORAGE_USER

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                             uri, None, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s


    def objectuser_create(self, args):
        '''
        Create user with the given details, which can
        subsequently be used to create its secret key.
        '''
        uid = args.uid
        namespace = args.namespace

        # users = self.objectuser_list(namespace)
        # for user in users:
        #     if(user == uid):
        #         raise SOSError(SOSError.ENTRY_ALREADY_EXISTS_ERR,
        #                        "Objectuser  create failed: object user " +
        #                        "with same name already exists")

        parms = {
            'user': uid,
            'namespace': namespace
        }

        profVers = config.get_profile_version()
        if profVers >= 3.1:
            if(args.tagset is not None):
                parms['tags'] = []
                for ts in args.tagset:
                    pair = ts.split('^')
                    if (len(pair)<2):
                        raise SOSError(SOSError.SOS_FAILURE_ERR, "A tagset must be a key value pair string delimited by '^'")
                    parms['tags'].append({"name" : pair[0], "value" : pair[1]})


        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                                             Objectuser.URI_WEBSTORAGE_USER, body, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s


    def objectuser_delete(self, uid, namespace):
        '''
        Deletes user and all its associated
        secret keys for the specified user details.
        '''

        parms = {
            'user': uid,
            'namespace': namespace
        }

        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                                             self.URI_WEBSTORAGE_USER_DEACTIVATE,
                                             body, None, xml)

        return


    def objectuser_lock(self, uid, namespace):
        return self.objectuser_locker(uid, namespace, 'true')


    def objectuser_unlock(self, uid, namespace):
        return self.objectuser_locker(uid, namespace, 'false')


    def objectuser_locker(self, uid, namespace, locked):
        '''
        Locks or unlocks specified user.
        '''

        parms = {
            'user': uid,
            'namespace': namespace,
            'isLocked': locked
        }

        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "PUT",
                                             self.URI_WEBSTORAGE_USER_LOCK,
                                             body, None, xml)

        return 


    def objectuser_getlock(self, uid, namespace=None):
        '''
        Gets the user lock details for the specified user name.
        '''

        uri = Objectuser.URI_WEBSTORAGE_USER_LOCK_INSTANCE.format(uid)

        if(namespace is not None):
            uri = uri + '/' + namespace

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                             uri, None, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s


    ################################################################
    ##
    ################################################################
    def objectuser_setusertags(self, args):
        uri = Objectuser.URI_WEBSTORAGE_USER_SET_TAG.format(args.uid)
        if(args.namespace is not None):
            uri = uri + '?namespace=' + args.namespace

        parms = {}
        if(args.tagset is not None):
            parms['tags'] = []
            for ts in args.tagset:
                pair = ts.split('^')
                if (len(pair)<2):
                    raise SOSError(SOSError.SOS_FAILURE_ERR, "A tagset must be a key value pair string delimited by '^'")
                parms['tags'].append({"name" : pair[0], "value" : pair[1]})

        body = json.dumps(parms)
        xml = False
        if self.__format == "xml":
            xml = True
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "PUT",
                                             uri,
                                             body, None, xml)
        return



    ################################################################
    ##
    ################################################################
    def objectuser_addusertags(self, args):
        uri = Objectuser.URI_WEBSTORAGE_USER_SET_TAG.format(args.uid)
        if(args.namespace is not None):
            uri = uri + '?namespace=' + args.namespace

        parms = {}
        if(args.tagset is not None):
            parms['tags'] = []
            for ts in args.tagset:
                pair = ts.split('^')
                if (len(pair)<2):
                    raise SOSError(SOSError.SOS_FAILURE_ERR, "A tagset must be a key value pair string delimited by '^'")
                parms['tags'].append({"name" : pair[0], "value" : pair[1]})

        body = json.dumps(parms)
        xml = False
        if self.__format == "xml":
            xml = True
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                                             uri,
                                             body, None, xml)
        return


    ################################################################
    ## used by other commands to see if user exists
    ################################################################
    def objectuser_query(self, uid, namespace=None):
        users = self.objectuser_list(None, namespace)

        for user in users['blobuser']:
            if( (user['userid'] == uid) and
               ( (namespace is None) or (user['namespace'] == namespace) ) ):
                return user

        err_str = "Object user query failed: object user with name " + \
                   uid + " not found"

        if(namespace is not None):
            err_str = err_str + " with namespace "+namespace

        raise SOSError(SOSError.NOT_FOUND_ERR, err_str)


    ################################################################
    ##
    ################################################################
    def objectuser_tagquery(self, args):
        uri = Objectuser.URI_WEBSTORAGE_USER_QUERY

        qparms = {}
        qparms['tag'] = args.tag
        if args.value is not None:
            qparms['value'] = args.value
        if args.marker is not None:
            qparms['marker'] = args.marker
        if args.limit is not None:
            qparms['limit'] = args.limit
        uri += '?' + urllib.urlencode(qparms)

        body = None
        xml = False
        if self.__format == "xml":
            xml = True
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                             uri,
                                             body, None, xml)

        print(s)
        if(self.__format == "json"):
            o = common.json_decode(s)
            #return common.format_json_object(o)
            return o
        return s



    ################################################################
    ##
    ################################################################
    def objectuser_getusertags(self, args):
        uri = Objectuser.URI_WEBSTORAGE_USER_SET_TAG.format(args.uid)

        if(args.namespace is not None):
            uri = uri + '?namespace=' + args.namespace

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                             uri, None, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s


    ################################################################
    ##
    ################################################################
    def objectuser_deleteusertags(self, args):
        uri = Objectuser.URI_WEBSTORAGE_USER_SET_TAG.format(args.uid)

        if(args.namespace is not None):
            uri = uri + '?namespace=' + args.namespace

    
        parms = {}
        if(args.tagset is not None):
            parms['tags'] = []
            for ts in args.tagset:
                pair = ts.split('^')
                if (len(pair)<2):
                    raise SOSError(SOSError.SOS_FAILURE_ERR, "A tagset must be a key value pair string delimited by '^'")
                parms['tags'].append({"name" : pair[0], "value" : pair[1]})

        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "DELETE",
                                             uri, body, None, xml)
        return


def create_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'create',
        description='ECS Objectuser Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create an objectuser')

    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='User identifier',
                                metavar='<uid>',
                                dest='uid',
                                required=True)


    mandatory_args.add_argument('-namespace', '-ns',
                                help='Namespace for user.',
                                default=None,
                                dest='namespace',
                                required=True)

    profVers = config.get_profile_version()
    if profVers >= 3.1:
        create_parser.add_argument('-tagset','-ts',
                                    help='List of one or more tagset tagname^tagvalue tuples ' +
                                         'eg list of tag^value',
                                    metavar='<tagset>',
                                    dest='tagset',
                                    default=None,
                                    nargs='*')


    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=objectuser_create)

def objectuser_create(args):

    obj = Objectuser(args.ip, args.port, args.format)

    try:
        res = obj.objectuser_create(args)
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e


def delete_parser(subcommand_parsers, common_parser):
    # delete command parser
    delete_parser = subcommand_parsers.add_parser(
        'delete',
        description='ECS Objectuser Delete CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Delete an objectuser')

    mandatory_args = delete_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='User identifer',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    mandatory_args.add_argument('-namespace', '-ns',
                                help='Namespace for user.',
                                default=None,
                                metavar='<namespace>',
                                dest='namespace',
                                required=True)

    delete_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    delete_parser.set_defaults(func=objectuser_delete)

def objectuser_delete(args):

    obj = Objectuser(args.ip, args.port, args.format)

    try:
        obj.objectuser_delete(args.uid, args.namespace)
        return 
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Objectuser delete failed: " + e.err_text)
        else:
            raise e


def list_parser(subcommand_parsers, common_parser):
    # list command parser
    list_parser = subcommand_parsers.add_parser(
        'list',
        description='ECS Objectuser List CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show Objectuser(s)')

    list_parser.add_argument('-uid', '-uid',
                             help='User identifier. Required if scope is USER.',
                             default=None,
                             metavar='<uid>',
                             dest='uid')

    list_parser.add_argument('-namespace', '-ns',
                            help='Namespace for user. Required if scope is USER or NAMESPACE',
                            default=None,
                            metavar='<namespace>',
                            dest='namespace')

    list_parser.add_argument('-format', '-f',
                            metavar='<format>', dest='format',
                            help='response format: xml or json (default:json)',
                            choices=['xml', 'json'],
                            default="json")

    list_parser.set_defaults(func=objectuser_list)

def objectuser_list(args):
    obj = Objectuser(args.ip, args.port, args.format)
    try:
        res = obj.objectuser_list(args.uid, args.namespace)
        '''
        # COMMENT PRE-04/18/2015
        #this is a pretty print output when a json object is received
        #it should probably be in its own function as it's not even for xml type results
        #I'm not sure that formatting is desired either
        res = res['blobuser']
        output = []

        for iter in res:
            tmp = dict()
            tmp['userid'] = iter['userid']
            tmp['namespace'] = iter['namespace']
            output.append(tmp)

        if(res):
            from common import TableGenerator
            TableGenerator(output, ['userid', 'namespace']).printTable()
        '''
        return res
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Objectuser list failed: " + e.err_text)
        else:
            raise e


def lock_parser(subcommand_parsers, common_parser):
    # lock command parser
    lock_parser = subcommand_parsers.add_parser(
        'lock',
        description='ECS Objectuser Lock CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Lock an objectuser')

    mandatory_args = lock_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='User identifier',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    mandatory_args.add_argument('-namespace', '-ns',
                                help='namespace',
                                metavar='<namespace>',
                                dest='namespace',
                                required=True)

    lock_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    lock_parser.set_defaults(func=objectuser_lock)

def objectuser_lock(args):

    obj = Objectuser(args.ip, args.port, args.format)

    try:
        res = obj.objectuser_lock(args.uid, args.namespace)
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user lock failed\n" + e.err_text)
        else:
            raise e


def unlock_parser(subcommand_parsers, common_parser):
    # add command parser
    unlock_parser = subcommand_parsers.add_parser(
        'unlock',
        description='ECS Objectuser unlock CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='unlock on an object user')

    mandatory_args = unlock_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='UID',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    mandatory_args.add_argument('-namespace', '-ns',
                                help='namespace',
                                metavar='<namespace>',
                                dest='namespace',
                                required=True)

    unlock_parser.add_argument('-format', '-f',
                               metavar='<format>', dest='format',
                               help='response format: xml or json (default:json)',
                               choices=['xml', 'json'],
                               default="json")

    unlock_parser.set_defaults(func=objectuser_unlock)

def objectuser_unlock(args):
    obj = Objectuser(args.ip, args.port, args.format)
    try:
        res = obj.objectuser_unlock(args.uid, args.namespace)
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": user unlock failed\n" + e.err_text)
        else:
            raise e


def getlock_parser(subcommand_parsers, common_parser):
    # get-lock command parser
    getlock_parser = subcommand_parsers.add_parser(
        'get-lock',
        description='ECS Objectuser get lock info CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show the lock for an Objectuser')

    mandatory_args = getlock_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='User identifier',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    getlock_parser.add_argument('-namespace', '-ns',
                                help='Namespace identifier for user',
                                default=None,
                                metavar='<namespace>',
                                dest='namespace')

    getlock_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    getlock_parser.set_defaults(func=objectuser_getlock)

def objectuser_getlock(args):

    obj = Objectuser(args.ip, args.port, args.format)

    try:
        res = obj.objectuser_getlock(args.uid, args.namespace)
        return res
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Objectuser delete failed: " + e.err_text)
        else:
            raise e


###################################################
##
###################################################
def setusertag_parser(subcommand_parsers, common_parser):
    setusertag_parser = subcommand_parsers.add_parser(
        'set-usertag',
        description='ECS Objectuser set user tag CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Sets user tags for an objectuser')

    mandatory_args = setusertag_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='User identifier',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    setusertag_parser.add_argument('-namespace', '-ns',
                                help='Namespace identifier for user',
                                default=None,
                                metavar='<namespace>',
                                dest='namespace')


    setusertag_parser.add_argument('-tagset','-ts',
                                help='List of one or more tagset tagname^tagvalue tuples ' +
                                     'eg list of tag^value',
                                metavar='<tagset>',
                                dest='tagset',
                                nargs='+')

    setusertag_parser.set_defaults(func=objectuser_setusertag)


###################################################
##
###################################################
def objectuser_setusertag(args):
    obj = Objectuser(args.ip, args.port)

    try:
        res = obj.objectuser_setusertags(args)
        return res
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Objectuser delete failed: " + e.err_text)
        else:
            raise e

###################################################
##
###################################################
def addusertag_parser(subcommand_parsers, common_parser):
    addusertag_parser = subcommand_parsers.add_parser(
        'add-usertag',
        description='ECS Objectuser add user tag CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Appends user tags for an objectuser')

    mandatory_args = addusertag_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='User identifier',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    addusertag_parser.add_argument('-namespace', '-ns',
                                help='Namespace identifier for user',
                                default=None,
                                metavar='<namespace>',
                                dest='namespace')


    addusertag_parser.add_argument('-tagset','-ts',
                                help='List of one or more tagset tagname^tagvalue tuples ' +
                                     'eg list of tag^value',
                                metavar='<tagset>',
                                dest='tagset',
                                nargs='+')

    addusertag_parser.set_defaults(func=objectuser_addusertag)

###################################################
##
###################################################
def objectuser_addusertag(args):
    obj = Objectuser(args.ip, args.port)

    try:
        res = obj.objectuser_addusertags(args)
        return res
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Objectuser delete failed: " + e.err_text)
        else:
            raise e




###################################################
##
###################################################
def queryuser_parser(subcommand_parsers, common_parser):
    query_parser = subcommand_parsers.add_parser(
        'query',
        description='ECS Objectuser set user tag CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='query for list of object users having tags')


    mandatory_args = query_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-tag', '-t',
                                help='the tag to use for the query search',
                                default=None,
                                dest='tag',
                                required=True)


    query_parser.add_argument('-value', '-v',
                                help='filter the query of the tag by its associated value',
                                default=None,
                                dest='value')


    query_parser.add_argument('-marker', '-m',
                                help='used to iterate through addl result set if limit is exceeded',
                                default=None,
                                dest='marker')


    query_parser.add_argument('-limit', '-l',
                                help='used to set the max number of items per result set',
                                default=None,
                                dest='limit')


    query_parser.add_argument('-namespace', '-ns',
                                help='Namespace identifier for user',
                                default=None,
                                metavar='<namespace>',
                                dest='namespace')


    query_parser.set_defaults(func=objectuser_tagquery)


###################################################
##
###################################################
def objectuser_tagquery(args):
    obj = Objectuser(args.ip, args.port)

    try:
        res = obj.objectuser_tagquery(args)
        return res
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Objectuser delete failed: " + e.err_text)
        else:
            raise e


###################################################
##
###################################################
def getusertag_parser(subcommand_parsers, common_parser):
    getusertag_parser = subcommand_parsers.add_parser(
        'get-usertag',
        description='ECS Objectuser get usertag objectuser CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='gets the user tags for an objectuser')

    mandatory_args = getusertag_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='User identifier',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    getusertag_parser.add_argument('-namespace', '-ns',
                                help='Namespace identifier for user',
                                default=None,
                                metavar='<namespace>',
                                dest='namespace')

    getusertag_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    getusertag_parser.set_defaults(func=objectuser_getusertags)

###################################################
##
###################################################
def objectuser_getusertags(args):
    obj = Objectuser(args.ip, args.port, args.format)

    try:
        res = obj.objectuser_getusertags(args)
        return res
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Objectuser delete failed: " + e.err_text)
        else:
            raise e



###################################################
##
###################################################
def deleteusertag_parser(subcommand_parsers, common_parser):
    deleteusertag_parser = subcommand_parsers.add_parser(
        'delete-usertag',
        description='ECS Objectuser delete usertag objectuser CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='deletes the user tags for an objectuser')

    mandatory_args = deleteusertag_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='User identifier',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    deleteusertag_parser.add_argument('-namespace', '-ns',
                                help='Namespace identifier for user',
                                default=None,
                                metavar='<namespace>',
                                dest='namespace')


    deleteusertag_parser.add_argument('-tagset','-ts',
                                help='List of one or more tagset tagname^tagvalue tuples ' +
                                     'eg list of tag^value',
                                metavar='<tagset>',
                                dest='tagset',
                                nargs='+')

    deleteusertag_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    deleteusertag_parser.set_defaults(func=objectuser_deleteusertags)

###################################################
##
###################################################
def objectuser_deleteusertags(args):
    obj = Objectuser(args.ip, args.port, args.format)

    try:
        obj.objectuser_deleteusertags(args)
        return 
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Objectuser delete failed: " + e.err_text)
        else:
            raise e


# Objectuser Main parser routine
def objectuser_parser(parent_subparser, common_parser):
    # main objectuser parser
    parser = parent_subparser.add_parser(
        'objectuser',
        description='ECS Objectuser CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on Objectuser')
    subcommand_parsers = parser.add_subparsers(help='Use One Of Commands')

    # create command parser
    create_parser(subcommand_parsers, common_parser)

    # delete command parser
    delete_parser(subcommand_parsers, common_parser)

    # list command parser
    list_parser(subcommand_parsers, common_parser)

    # lock command parser
    lock_parser(subcommand_parsers, common_parser)

    # get-lock command parser
    getlock_parser(subcommand_parsers, common_parser)

    # unlock command parser
    unlock_parser(subcommand_parsers, common_parser)

    profVers = config.get_profile_version()
    if profVers >= 3.1:
        addusertag_parser(subcommand_parsers, common_parser)
        setusertag_parser(subcommand_parsers, common_parser)
        getusertag_parser(subcommand_parsers, common_parser)
        deleteusertag_parser(subcommand_parsers, common_parser)
        queryuser_parser(subcommand_parsers, common_parser)
