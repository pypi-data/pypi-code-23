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
"""Elasticsearch upd backend
$Id: backend.py 4742 2018-02-10 16:46:47Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import sys
import os.path
import logging
import traceback

import elasticsearch

try:
    import p01.geo
    import p01.geo.locator
    GEOLOCATE = True
except ImportError:
    GEOLOCATE = False

# priority: ujson > simplejson > jsonlib2 > json
priority = ['ujson', 'simplejson', 'jsonlib2', 'json']
for mod in priority:
    try:
        json = __import__(mod)
    except ImportError:
        pass
    else:
        break


logger = logging.getLogger('p01.kibana.backend')


class ElasticSearchBackend(object):
    """Sends event data to one or more elasticsearch server"""

    locator = None

    def __init__(self, server, esoptions, maxminddb=None, maxitems=1000000):
        self.server = server
        self._hosts = esoptions.get('hosts')
        self.es = elasticsearch.Elasticsearch(**esoptions)
        if GEOLOCATE:
            if maxminddb is None:
                maxminddb = os.path.join(os.path.dirname(p01.geo.__file__),
                    'data', 'GeoLite2-City.mmdb')
            cache = p01.geo.locator.MaxItemCache(maxitems=maxitems)
            self.locator = p01.geo.locator.GeoLocator(maxminddb, cache=cache)
            sys.stderr.write("Locator loaded: %s\n" % maxminddb)
        else:
            sys.stderr.write("Locator: p01.geo package not available\n")

    def locate(self, source):
        """Locate geo data based on available ip address if maxmind is enabled
        """
        try:
            ip = source['address']
            obj = self.locator.getData(ip)
            source['geo'] = {
                'continent': obj.continent,
                'country': obj.countryCode,
                'countryName': obj.countryName,
                # lonlat, longitude and latitude (order matters)
                'state': obj.metroCode,
                'zip': obj.postalCode,
                'city': obj.city,
                'cityGeoName': obj.cityGeoName,
                'timezone': obj.tzName,
            }
            lon = obj.longitude
            lat = obj.latitude
            if lon is not None and lat is not None:
                # Format in [lon, lat], note, the order of lon/lat here in
                # order to conform with GeoJSON.
                source['geo']['coordinates'] = [float(lon), float(lat)]
        except StandardError, ex:
            # no locator, no request ip, not found geo data. Just never fail
            # but raise on KeyboardInterrupt
            pass

    def send(self, iterable):
        """Send messages to elasticsearch server

        We received the following data from our client. See KibanaClient and
        KibanaServer:

        {
            '_index': '...',
            '_type': '...',
            '_source': {
                '@version': '...',
                '@timestamp': '...',
                'message': '...'
            }
        }

        """
        for data in iterable:
            try:
                index = data['_index']
                doc_type = data['_type']
                source = data['_source']
                if hasattr(source, 'encode'):
                    source = source.encode('utf-8')
                self.locate(source)
                self.es.index(index, doc_type, source)
            except StandardError, ex:
                # ConnectionError etc. but raise on KeyboardInterrupt
                extra = {'data': "Data: %s" % json.dumps(data)}
                logger.exception(ex, extra=extra)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, ','.join(self._hosts))
