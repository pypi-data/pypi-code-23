##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""A pymongo client with environment based setup
$Id: client.py 4715 2018-01-29 16:12:57Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import pymongo


###############################################################################
#
# pymongo client setup


def getMongoClient(settings=None, connect=True, retry=True):
    if settings is None:
        import settings
        settings = settings
    uri = settings.MONGODB_URI
    if uri == 'testing':
        # fake mongodb is only used for xspider testing
        import m01.mongo.testing
        return m01.mongo.testing.FakeMongoConnectionPool().connection
    elif settings.P01_CDN_RECIPE_PROCESS:
        # resource extraction, just a dumy client using testing port
        return pymongo.MongoClient('localhost:45017')
    else:
        uri = str(uri)
        if settings.MONGODB_SSL and \
            settings.MONGODB_SSL_CERT_REQUIRED is None:
            # if undefined use ssl.CERT_REQUIRED
            import ssl
            ssl_cert_reqs = ssl.CERT_REQUIRED
        else:
            ssl_cert_reqs = settings.MONGODB_SSL_CERT_REQUIRED
        if not settings.MONGODB_CONNECT:
            connect = False
        options = {
            'connect': connect,
            'tz_aware': settings.MONGODB_TZ_AWARE,
        }
        if settings.MONGODB_REPLICA_SET:
            options['replicaSet'] = settings.MONGODB_REPLICA_SET
        if settings.MONGODB_APP_NAME:
            options['appname'] = settings.MONGODB_APP_NAME
        if settings.MONGODB_MIN_POOL_SIZE:
            options['minPoolSize'] = settings.MONGODB_MIN_POOL_SIZE
        if settings.MONGODB_MAX_POOL_SIZE:
            options['maxPoolSize'] = settings.MONGODB_MAX_POOL_SIZE
        if settings.MONGODB_CONNECT_TIMEOUT:
            options['connectTimeoutMS'] = \
                settings.MONGODB_CONNECT_TIMEOUT
        if settings.MONGODB_SERVER_SELECTION_TIMEOUT:
            options['serverSelectionTimeoutMS'] = \
                settings.MONGODB_SERVER_SELECTION_TIMEOUT
        if settings.MONGODB_SOCKET_TIMEOUT:
            options['socketTimeoutMS'] = settings.MONGODB_SOCKET_TIMEOUT
        if settings.MONGODB_WAIT_QUEUE_TIMEOUT:
            options['waitQueueTimeoutMS'] = \
                settings.MONGODB_WAIT_QUEUE_TIMEOUT
        if settings.MONGODB_MAX_IDLE_TIME_MS:
            options['maxIdleTimeMS'] = \
                settings.MONGODB_MAX_IDLE_TIME_MS
        if settings.MONGODB_WAIT_QUEUE_MULTIPLE:
            options['waitQueueMultiple'] = \
                settings.MONGODB_WAIT_QUEUE_MULTIPLE
        if settings.MONGODB_HEARTBEAT_FREQUENCY:
            options['heartbeatFrequencyMS'] = \
                settings.MONGODB_HEARTBEAT_FREQUENCY
        # auth options
        if settings.MONGODB_AUTH_MECHNISM:
            options['authMechanism'] = settings.MONGODB_AUTH_MECHNISM
        if settings.MONGODB_USERNAME:
            options['username'] = settings.MONGODB_USERNAME
        if settings.MONGODB_PASSWORD:
            options['password'] = settings.MONGODB_PASSWORD
        # ssl options
        if settings.MONGODB_SSL:
            options['ssl'] = settings.MONGODB_SSL
            if ssl_cert_reqs:
                options['ssl_cert_reqs'] = ssl_cert_reqs
            if settings.MONGODB_CA_CERT:
                options['ssl_ca_certs'] = settings.MONGODB_CA_CERT
            if settings.MONGODB_CLIENT_CERT:
                options['ssl_certfile'] = settings.MONGODB_CLIENT_CERT
            if settings.MONGODB_PEM_PASSPHRASE:
                options['ssl_pem_passphrase'] = settings.MONGODB_PEM_PASSPHRASE
            if settings.MONGODB_CLIENT_CERT:
                options['ssl_crlfile'] = settings.MONGODB_REVOCATION_LIST
            if settings.MONGODB_SSL_MATCH_HOSTNAME:
                options['ssl_match_hostname'] = \
                    settings.MONGODB_SSL_MATCH_HOSTNAME
        try:
            client = pymongo.MongoClient(uri, **options)
            if connect:
                client.admin.command('ismaster')
            return client
        except pymongo.errors.ConnectionFailure as e:
            # ensure client, try again without connect
            if retry:
                return getMongoClient(settings, connect=False, retry=False)
            else:
                raise e
