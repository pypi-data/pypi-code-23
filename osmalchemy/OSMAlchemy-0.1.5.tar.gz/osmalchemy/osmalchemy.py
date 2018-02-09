# ~*~ coding: utf-8 ~*~
#-
# OSMAlchemy - OpenStreetMap to SQLAlchemy bridge
# Copyright (c) 2016, 2017 Dominik George <nik@naturalnet.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Alternatively, you are free to use OSMAlchemy under Simplified BSD, The
# MirOS Licence, GPL-2+, LGPL-2.1+, AGPL-3+ or the same terms as Python
# itself.

""" Module that holds the main OSMAlchemy class.

The classe encapsulates the model and accompanying logic.
"""

from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
try:
    from flask_sqlalchemy import SQLAlchemy as FlaskSQLAlchemy
except ImportError:
    # non-fatal, Flask-SQLAlchemy support is optional
    # Create stub to avoid bad code later on
    class FlaskSQLAlchemy(object):
        pass

from .model import _generate_model
from .util.db import _import_osm_file
from .util.online import _generate_overpass_api
from .triggers import _generate_triggers

class OSMAlchemy(object):
    """ Wrapper class for the OSMAlchemy model and logic

    This class holds all the SQLAlchemy classes and logic that make up
    OSMAlchemy. It is contained in a separate class because it is a
    template that can be modified as needed by users, e.g. by using a
    different table prefix or a different declarative base.
    """

    def __init__(self, sa=None, prefix="osm_", overpass=None, maxage=60*60*24):
        """ Initialise the table definitions in the wrapper object

        This function generates the OSM element classes as SQLAlchemy table
        declaratives.

        Positional arguments:

          sa - reference to SQLAlchemy stuff; can be either of…
                 …an Engine instance, or…
                 …a tuple of (Engine, Base), or…
                 …a tuple of (Engine, Base, ScopedSession), or…
                 …a Flask-SQLAlchemy instance.
          prefix - optional; prefix for table names, defaults to "osm_"
          overpass - optional; API endpoint URL for Overpass API. Can be…
                      …None to disable loading data from Overpass (the default), or…
                      …True to enable the default endpoint URL, or…
                      …a string with a custom endpoint URL.
          maxage - optional; the maximum age after which elements are refreshed from
                   Overpass, in seconds, defaults to 86400s (1d)
        """

        # Store logger or create mock
        import logging
        self.logger = logging.getLogger('osmalchemy')
        self.logger.addHandler(logging.NullHandler())

        # Create fields for SQLAlchemy stuff
        self.base = None
        self.engine = None
        self.session = None

        # Store prefix
        self.prefix = prefix

        # Store maxage
        self.maxage = maxage

        if sa is not None:
            self.init_app(sa)

        # Store API endpoint for Overpass
        if not overpass is None:
            if overpass is True:
                # Use default endpoint URL from overpass module
                self.overpass = _generate_overpass_api()
                self.logger.debug("Overpass API enabled with default endpoint.")
            elif isinstance(overpass, str):
                # Pass given argument as custom URL
                self.overpass = _generate_overpass_api(overpass)
                self.logger.debug("Overpass API enabled with endpoint %s." % overpass)
            else:
                # We got something unknown passed, bail out
                raise TypeError("Invalid argument passed to overpass parameter.")
        else:
            # Do not use overpass
            self.overpass = None

        # Add triggers if online functionality is enabled
        if not self.overpass is None:
            _generate_triggers(self)
            self.logger.debug("Triggers generated and activated.")

    def init_app(self, sa):
        # Inspect sa argument
        if isinstance(sa, tuple):
            # Got tuple of (Engine, Base) or (Engine, Base, ScopedSession)
            self.engine = sa[0]
            self.base = sa[1]
            if len(sa) == 3:
                self.session = sa[2]
            else:
                self.session = scoped_session(sessionmaker(bind=self.engine))
            self.logger.debug("Called with (engine, base, session) tuple.")
        elif isinstance(sa, Engine):
            # Got a plain engine, so derive the rest from it
            self.engine = sa
            self.base = declarative_base(bind=self.engine)
            self.session = scoped_session(sessionmaker(bind=self.engine))
            self.logger.debug("Called with a plain SQLAlchemy engine.")
        elif isinstance(sa, FlaskSQLAlchemy):
            # Got a Flask-SQLAlchemy instance, extract everything from it
            self.base = sa.Model
            self.session = sa.session
            self.logger.debug("Called with a Flask-SQLAlchemy wrapper.")
        else:
            # Something was passed, but none of the expected argument types
            raise TypeError("Invalid argument passed to sa parameter.")

        # Generate model and store as instance members
        self.node, self.way, self.relation, self.element, self.tag, self.cached_query = _generate_model(self)
        self.logger.debug("Generated OSMAlchemy model with prefix %s." % self.prefix)

    def import_osm_file(self, path):
        """ Import data from an OSM XML file into this model.

          path - path to the file to import
        """

        # Call utility funtion with own reference and session
        _import_osm_file(self, path)

    def create_api(self, api_manager):
        """ Create Flask-Restless API endpoints. """

        def _expand_tags(obj):
            # Type name to object mapping
            _types = {
                      "node": self.node,
                      "way": self.way,
                      "relation": self.relation
                     }

            # Get tags dictionary from ORM object
            instance = self.session.query(_types[obj["type"]]).get(obj["element_id"])

            # Fill a tag dictionary
            res = {}
            for key in obj["tags"]:
                res[key] = instance.tags[key]

            # Replace tags list with generated dictionary
            obj["tags"] = res

        def _cleanup(obj):
            # Remove unnecessary entries from dict
            del obj["osm_elements_tags"]
            del obj["type"]

        def _post_get(result, **_):
            # Post-processor for GET
            # Work-around for strange bug in Flask-Restless preventing detection
            #  of dictionary-like association proxies
            if "objects" in result:
                # This is a GET_MANY call
                for obj in result["objects"]:
                    _expand_tags(obj)
                    _cleanup(obj)
            else:
                # This is a GET_SINGLE call
                _expand_tags(result)
                _cleanup(result)

        # Define post-processors for all collections
        postprocessors = {"GET_SINGLE": [_post_get], "GET_MANY": [_post_get]}

        # Define collections for all object types
        api_manager.create_api(self.node, postprocessors=postprocessors)
        api_manager.create_api(self.way, postprocessors=postprocessors)
        api_manager.create_api(self.relation, postprocessors=postprocessors)
