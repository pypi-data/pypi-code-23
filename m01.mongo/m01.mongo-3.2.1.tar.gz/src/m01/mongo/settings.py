##############################################################################
#
# Copyright (c) 2016 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Settings
$Id: settings.py 4715 2018-01-29 16:12:57Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import pymongo.common

import m01.mongo.env


################################################################################
#
# mongodb
#
# MONGODB_URI = "mongodb://admin:password@127.0.0.1:27017"
#
# NOTE: MONGODB_URI Port: 45017 is used for testing
#       use your own mongodb uri in your own setup for set the corret uri e.g:
#
#       MONGODB_URI = 127.0.0.1:27017
#       or
#       MONGODB_URI = "mongodb://username:password@127.0.0.1:27017"
#
#       or use the environment variable setup if you need a certificate based
#       setup

MONGODB_URI = "127.0.0.1:27017"
MONGODB_CONNECT = True
MONGODB_REPLICA_SET = None
MONGODB_TZ_AWARE = True
MONGODB_APP_NAME = None

# timeout options
MONGODB_MIN_POOL_SIZE = pymongo.common.MIN_POOL_SIZE
MONGODB_MAX_POOL_SIZE = pymongo.common.MAX_POOL_SIZE
MONGODB_CONNECT_TIMEOUT = pymongo.common.CONNECT_TIMEOUT * 1000
MONGODB_SERVER_SELECTION_TIMEOUT = pymongo.common.SERVER_SELECTION_TIMEOUT * 1000
MONGODB_SOCKET_TIMEOUT = 20 * 1000
MONGODB_WAIT_QUEUE_TIMEOUT = 20 * 1000
MONGODB_MAX_IDLE_TIME_MS = pymongo.common.MAX_IDLE_TIME_MS
MONGODB_WAIT_QUEUE_MULTIPLE = None
MONGODB_HEARTBEAT_FREQUENCY = pymongo.common.MIN_HEARTBEAT_INTERVAL * 1000

# ssl options
MONGODB_SSL = False
MONGODB_SSL_CERT_REQUIRED = None
MONGODB_SSL_MATCH_HOSTNAME = True
MONGODB_CA_CERT = None
MONGODB_CLIENT_CERT = None
MONGODB_PEM_PASSPHRASE = None
MONGODB_REVOCATION_LIST_FILE = None

# auth options
MONGODB_AUTH_MECHNISM = None
MONGODB_USERNAME = None
MONGODB_PASSWORD = None


# uri, replica set
MONGODB_URI = m01.mongo.env.getEnviron('MONGODB_URI', default=MONGODB_URI)
MONGODB_CONNECT = m01.mongo.env.getEnviron('MONGODB_CONNECT', rType=bool,
    default=MONGODB_CONNECT)
MONGODB_REPLICA_SET = m01.mongo.env.getEnviron('MONGODB_REPLICA_SET',
    default=MONGODB_REPLICA_SET)
MONGODB_TZ_AWARE = m01.mongo.env.getEnviron('MONGODB_TZ_AWARE', rType=bool,
    default=MONGODB_TZ_AWARE)
MONGODB_APP_NAME = m01.mongo.env.getEnviron('MONGODB_APP_NAME',
    default=MONGODB_APP_NAME)

# timeout options
MONGODB_CONNECT_TIMEOUT = m01.mongo.env.getEnviron('MONGODB_CONNECT_TIMEOUT',
    rType=int, default=MONGODB_CONNECT_TIMEOUT)
MONGODB_SERVER_SELECTION_TIMEOUT = m01.mongo.env.getEnviron(
    'MONGODB_SERVER_SELECTION_TIMEOUT', rType=int,
    default=MONGODB_SERVER_SELECTION_TIMEOUT)
MONGODB_SOCKET_TIMEOUT = m01.mongo.env.getEnviron('MONGODB_SOCKET_TIMEOUT',
    rType=int, default=MONGODB_SOCKET_TIMEOUT)
MONGODB_WAIT_QUEUE_TIMEOUT = m01.mongo.env.getEnviron(
    'MONGODB_WAIT_QUEUE_TIMEOUT', rType=int, default=MONGODB_WAIT_QUEUE_TIMEOUT)
MONGODB_MAX_IDLE_TIME_MS = m01.mongo.env.getEnviron(
    'MONGODB_MAX_IDLE_TIME_MS', rType=int, default=MONGODB_MAX_IDLE_TIME_MS)
MONGODB_MIN_POOL_SIZE = m01.mongo.env.getEnviron(
    'MONGODB_MIN_POOL_SIZE', rType=int, default=MONGODB_MIN_POOL_SIZE)
MONGODB_MAX_POOL_SIZE = m01.mongo.env.getEnviron(
    'MONGODB_MAX_POOL_SIZE', rType=int, default=MONGODB_MAX_POOL_SIZE)
MONGODB_HEARTBEAT_FREQUENCY = m01.mongo.env.getEnviron(
    'MONGODB_HEARTBEAT_FREQUENCY', rType=int,
    default=MONGODB_HEARTBEAT_FREQUENCY)
MONGODB_WAIT_QUEUE_MULTIPLE = m01.mongo.env.getEnviron('MONGODB_WAIT_QUEUE_MULTIPLE',
    default=MONGODB_WAIT_QUEUE_MULTIPLE)

# ssl options
MONGODB_SSL = m01.mongo.env.getEnviron('MONGODB_SSL', rType=bool,
    default=MONGODB_SSL)
MONGODB_SSL_CERT_REQUIRED = m01.mongo.env.getEnviron(
    'MONGODB_SSL_CERT_REQUIRED', rType=bool, default=MONGODB_SSL_CERT_REQUIRED)
MONGODB_SSL_MATCH_HOSTNAME = m01.mongo.env.getEnviron(
    'MONGODB_SSL_MATCH_HOSTNAME', rType=bool,
    default=MONGODB_SSL_MATCH_HOSTNAME)
MONGODB_CA_CERT = m01.mongo.env.getEnviron('MONGODB_CA_CERT',
    rType='path', default=MONGODB_CA_CERT)
MONGODB_CLIENT_CERT = m01.mongo.env.getEnviron('MONGODB_CLIENT_CERT',
    rType='path', default=MONGODB_CLIENT_CERT)
MONGODB_PEM_PASSPHRASE = m01.mongo.env.getEnviron('MONGODB_PEM_PASSPHRASE',
    default=MONGODB_PEM_PASSPHRASE)
MONGODB_REVOCATION_LIST_FILE = m01.mongo.env.getEnviron(
    'MONGODB_REVOCATION_LIST_FILE', rType='path',
    default=MONGODB_REVOCATION_LIST_FILE)

# auth options
MONGODB_AUTH_MECHNISM = m01.mongo.env.getEnviron('MONGODB_AUTH_MECHNISM',
    default=MONGODB_AUTH_MECHNISM)
MONGODB_USERNAME = m01.mongo.env.getEnviron('MONGODB_USERNAME',
    default=MONGODB_USERNAME)
MONGODB_PASSWORD = m01.mongo.env.getEnviron('MONGODB_PASSWORD',
    default=MONGODB_PASSWORD)


# support p01.cdn extraction
P01_CDN_RECIPE_PROCESS = m01.mongo.env.getEnviron('P01_CDN_RECIPE_PROCESS',
    required=False, default=False)