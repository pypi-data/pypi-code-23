###############################################################################
#
# Copyright (c) 2013 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""Start script and config
$$
"""
__docformat__ = "reStructuredText"

import sys
import json
import socket
import traceback
import optparse
import os.path

import p01.kibana.server
import p01.kibana.logger


################################################################################
#
# options

def get_options(args=None):
    if args is None:
        args = sys.argv
    original_args = args
    parser = optparse.OptionParser(usage=("usage: <script> [options]"))
    # udp interface
    parser.add_option('--interface', dest='interface',
        help="interface [host]:port (defaults to 0.0.0.0:2200)",
        default=p01.kibana.server.INTERFACE,
        )
    # elasticsearch backend
    parser.add_option('--elasticsearch', dest='elasticsearch',
        help="a elasticsearch backend  [host]:port (defaults to 0.0.0.0:9200)",
        default=p01.kibana.server.ELASTICSERACH_URI,
        )
    parser.add_option('--elasticsearch-use-ssl', dest='elasticsearch_use_ssl',
        action="store_true", help="elasticsearch use ssl",
        default=p01.kibana.server.ELASTICSEARCH_USE_SSL,
        )
    parser.add_option('--elasticsearch-ca-certs', dest='elasticsearch_ca_certs',
        help="elasticsearch ca cert path",
        default=p01.kibana.server.ELASTICSEARCH_CA_CERT,
        )
    parser.add_option('--elasticsearch-client-cert',
        dest='elasticsearch_client_cert',
        help="elasticsearch client cert path",
        default=p01.kibana.server.ELASTICSEARCH_CLIENT_CERT,
        )
    parser.add_option('--elasticsearch-client-key',
        dest='elasticsearch_client_key',
        help="elasticsearch client cert key path",
        default=p01.kibana.server.ELASTICSEARCH_CLIENT_CERT_KEY,
        )
    parser.add_option('--elasticsearch-verify-certs',
        dest='elasticsearch_verify_certs', action="store_true",
        help="elasticsearch client verify certs",
        default=p01.kibana.server.ELASTICSEARCH_VERIFY_CERTS,
        )
    parser.add_option('--elasticsearch-client-username',
        dest='elasticsearch_client_username',
        help="elasticsearch client username",
        default=p01.kibana.server.ELASTICSEARCH_CLIENT_USERNAME,
        )
    parser.add_option('--elasticsearch-client-password',
        dest='elasticsearch_client_password',
        help="elasticsearch client password",
        default=p01.kibana.server.ELASTICSEARCH_CLIENT_PASSWORD,
        )
    parser.add_option('--elasticsearch-client-credentials',
        dest='elasticsearch_client_credentials',
        help="elasticsearch client credentials file path containing {username:password}",
        default=p01.kibana.server.ELASTICSEARCH_CLIENT_CREDENTIALS_PATH,
        )
    parser.add_option('--elasticsearch-ssl-version',
        dest='elasticsearch_ssl_version',
        help="elasticsearch ssl version",
        default=p01.kibana.server.ELASTICSEARCH_SSL_VERSION,
        )
    parser.add_option('--elasticsearch-ssl-assert-hostname',
        dest='elasticsearch_ssl_assert_hostname', action="store_true",
        help="elasticsearch assert hostname",
        default=p01.kibana.server.ELASTICSEARCH_SSL_ASSERT_HOSTNAME,
        )
    parser.add_option('--elasticsearch-ssl-assert-fingerprint',
        dest='elasticsearch_ssl_assert_fingerprint', action="store_true",
        help="elasticsearch assert fingerprint",
        default=p01.kibana.server.ELASTICSEARCH_SSL_ASSERT_FINGERPRINT,
        )
    parser.add_option('--elasticsearch-max-size',
        dest='elasticsearch_client_max_size',
        help="elasticsearch client max size",
        default=p01.kibana.server.ELASTICSEARCH_MAXSIZE,
        )
    parser.add_option('--elasticsearch-timeout', dest='elasticsearch_timeout',
        default=p01.kibana.server.ELASTICSERACH_TIMEOUT,
        help="elasticsearch connection timeout, in seconds (default %s)" % (
            p01.kibana.server.ELASTICSERACH_TIMEOUT),
        )
    parser.add_option('--elasticsearch-sniff-on-start',
        dest='elasticsearch_sniff_on_start', action="store_true",
        help="elasticsearch sniff on start",
        default=p01.kibana.server.ELASTICSEARCH_SNIFF_ON_START,
        )
    parser.add_option('--elasticsearch-sniff-on-connection-fail',
        dest='elasticsearch_sniff_on_connection_fail', action="store_true",
        help="elasticsearch sniff on connection fail",
        default=p01.kibana.server.ELASTICSEARCH_SNIFF_ON_CONNECTION_FAIL,
        )
    parser.add_option('--elasticsearch-sniff-timeout',
        dest='elasticsearch_client_sniff_timeout',
        help="elasticsearch client max size",
        default=p01.kibana.server.ELASTICSEARCH_SNIFF_TIMEOUT,
        )
    parser.add_option('--elasticsearch-sniffer-timeout',
        dest='elasticsearch_client_sniffer_timeout',
        help="elasticsearch client sniffer timeout",
        default=p01.kibana.server.ELASTICSEARCH_SNIFFER_TIMEOUT,
        )
    parser.add_option('--elasticsearch-loglevel',
        dest='elasticsearch_client_loglevel',
        help="elasticsearch client log level",
        default=p01.kibana.server.ELASTICSERACH_LOGLEVEL,
        )
    # udp server
    parser.add_option('--interval', dest='interval',
        default=p01.kibana.server.INTERVAL,
        help="flush interval, in seconds (default %s)" % (
            p01.kibana.server.INTERVAL),
        )
    parser.add_option('--max-queue-size', dest='maxQueueSize', type='int',
        help="max (message) queue size (default=1000)",
        default=p01.kibana.server.MAX_QUEUE_SIZE,
        )
    parser.add_option('--max-batch-size', dest='maxBatchSize', type='int',
        help="max (log event) batch size (default=250)",
        default=p01.kibana.server.MAX_QUEUE_SIZE,
        )
    parser.add_option('--loglevel', dest='loglevel', type='int',
        help="python logging level (default=40) (40=ERROR)",
        default=p01.kibana.server.LOG_LEVEL,
        )
    parser.add_option('--trace', dest='trace', action="store_true",
        help="add logging handler for elasticsearch.trace",
        default=p01.kibana.server.TRACE,
        )
    parser.add_option('--debug', dest='debug', action="store_true",
        help="Enable debug output",
        default=p01.kibana.server.DEBUG,
        )
    # maxmind database settings
    parser.add_option('--maxminddb', dest='maxminddb',
        help="Maxmind database path otherwise default database get used",
        default=None,
        )
    parser.add_option('--maxitems', dest='maxitems', type='int',
        help="Max cached maxmind geo data items",
        default=p01.kibana.server.MAX_GEO_DATA_ITEMS
        )
    options, positional = parser.parse_args(args)
    options.original_args = original_args
    options.loglevel = p01.kibana.logger.getLoggingLevel(options.loglevel)
    return options


################################################################################
#
# helper methods

def getHosts(value):
    if ',' in value:
        hosts = value.split(',')
    elif isinstance(value, basestring) and value:
        hosts = [value]
    elif isinstance(value, (list, tuple)):
        hosts = list(hosts)
    else:
        hosts = ['0.0.0.0:9200']
    return hosts


def checkPath(key, path):
    """Check given path"""
    if path is None or not os.path.exists(path):
        raise ValueError(
            "Path \"%s\" for option \"%s\" does not exist" % (
            path, key))


def getAuthenticationCredentials(path):
    """Get credentials form file by given path

    The file must provide the username and password as json data e.g.
    {
        'username': 'john',
        'password': 'password'
    }

    """
    checkPath('--elasticsearch-client-credentials', path)
    with open(path, 'rb') as f:
        credentials = json.loads(f.read())
        return credentials['username'], credentials['password']


################################################################################
#
# start script

def main(args=None):
    # get options
    options = get_options(args)
    # setup logging
    p01.kibana.logger.setUpLogger(options)
    try:
        # stops with signal.SIGINT on KeyboardInterrupt
        # XXX: seems that circus does not catch stdout during startup
        #      Also during stop a server with circus will the log get ignored
        #      just use stderr, that's what the circus daemon will listen on
        #      startup a watcher
        sys.stderr.write("Starting server\n")
        hosts = getHosts(options.elasticsearch)
        try:
            timeout = float(options.elasticsearch_timeout)
        except Exception:
            timeout = 10.0
        esoptions = {
            'hosts': hosts,
            'maxsize': options.elasticsearch_client_max_size,
            'logLevel': options.elasticsearch_client_loglevel,
            'timeout': timeout,
            # sniff before doing anything
            # XXX: sniff fails, do not sniff we use fixed IP addreses.
            # This means we need to update the app if we add more nodes
            'sniff_on_start': \
                options.elasticsearch_sniff_on_start,
            # refresh nodes after a node fails to respond
            'sniff_on_connection_fail': \
                options.elasticsearch_sniff_on_connection_fail,
             # set sniffing request timeout to 10 seconds
            'sniff_timeout': options.elasticsearch_client_sniff_timeout,
            # and also every 60 seconds
            'sniffer_timeout': options.elasticsearch_client_sniffer_timeout,
        }
        # setup auth credentials
        credentials = options.elasticsearch_client_credentials
        if credentials is not None:
            esoptions['http_auth'] = getAuthenticationCredentials(credentials)

        elif options.elasticsearch_client_username and \
            options.elasticsearch_client_password:
            esoptions['http_auth']  = (
                options.elasticsearch_client_username,
                options.elasticsearch_client_password,
                )

        # add optional elasticsearch settings
        if options.elasticsearch_use_ssl:
            esoptions['use_ssl']  = options.elasticsearch_use_ssl
        if options.elasticsearch_ca_certs is not None:
            # optional path to CA bundle
            checkPath('--elasticsearch-ca-certs', options.elasticsearch_ca_certs)
            esoptions['ca_certs']  = options.elasticsearch_ca_certs
        if options.elasticsearch_client_cert is not None:
            # path to the file containing the private key and the certificate,
            # or cert only if using client_key
            checkPath('--elasticsearch-client-cert',
                options.elasticsearch_client_cert)
            esoptions['client_cert']  = options.elasticsearch_client_cert
        if options.elasticsearch_client_key is not None:
            # path to the file containing the private key if using separate
            # cert and key files (client_cert will contain only the cert)
            checkPath('--elasticsearch-client-key',
                options.elasticsearch_client_key)
            esoptions['client_key']  = options.elasticsearch_client_key
        if options.elasticsearch_verify_certs is not None:
            esoptions['verify_certs']  = options.elasticsearch_verify_certs
        if options.elasticsearch_ssl_version is not None:
            # version of the SSL protocol to use. Choices are: SSLv23 (default)
            # SSLv2 SSLv3 TLSv1 (see PROTOCOL_* constants in the ssl module for
            # exact options for your environment).
            # ssl_version='SSLv23'
            esoptions['ssl_version']  = options.elasticsearch_ssl_version
            # use hostname verification if not `False`
            # we use client as CN (commonName) in ca subject
        if options.elasticsearch_ssl_assert_hostname is not None:
            esoptions['ssl_assert_hostname']  = \
                options.elasticsearch_ssl_assert_hostname
            # verify the supplied certificate fingerprint if not None
        if options.elasticsearch_ssl_assert_fingerprint is not None:
            esoptions['ssl_assert_fingerprint']  = \
                options.elasticsearch_ssl_assert_fingerprint
        # setup server
        if options.maxminddb is not None:
            checkPath('--maxminddb', options.maxminddb)
            maxminddb = options.maxminddb
        else:
            maxminddb = None
        server = p01.kibana.server.KibanaServer(options.interface,
            # elasticsearch settings
            esoptions,
            # udp server options
            interval=options.interval,
            maxQueueSize=options.maxQueueSize,
            maxBatchSize=options.maxBatchSize,
            # maxmind settings
            maxminddb=maxminddb,
            maxitems=options.maxitems,
            # logging options
            debug=options.debug,
            loglevel=options.loglevel)
        sys.stderr.write("Server started at: %s\n" % options.interface)
        sys.stderr.write("Elasticsarch used: %s\n" % options.elasticsearch)
        if options.debug:
            sys.stderr.write("Debugging: on\n")
        server.start()
    except KeyboardInterrupt:
        server.stop()
    except Exception, e:
        sys.stderr.write("interface: %s\n" % options.interface)
        sys.stderr.write("backend: %s\n" % options.elasticsearch)
        sys.stderr.write("interval: %s\n" % options.interval)
        sys.stderr.write("maxQueueSize: %s\n" % options.maxQueueSize)
        sys.stderr.write("loglevel: %s\n" % options.loglevel)
        sys.stderr.write("args: %s\n" % options.original_args)
        traceback.print_exc()
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
