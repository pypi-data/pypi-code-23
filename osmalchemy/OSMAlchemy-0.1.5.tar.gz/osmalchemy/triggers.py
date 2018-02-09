# ~*~ coding: utf-8 ~*~
#-
# OSMAlchemy - OpenStreetMap to SQLAlchemy bridge
# Copyright (c) 2016 Dominik George <nik@naturalnet.de>
# Copyright (c) 2016 Eike Tim Jesinghaus <eike@naturalnet.de>
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

""" Trigger code for live OSMAlchemy/Overpass integration. """

import datetime
from hashlib import md5
from sqlalchemy import inspect
from sqlalchemy.event import listens_for
from sqlalchemy.orm import Query
from weakref import WeakSet

from .util.db import _import_osm_xml
from .util.online import (_get_elements_by_query, _where_to_tree,
                          _trees_to_overpassql, _normalise_overpassql,
                          _get_single_element_by_id)

def _generate_triggers(oa):
    """ Generates the triggers for online functionality.

      oa - reference to the OSMAlchemy instance to be configured
    """

    _visited_queries = WeakSet()

    @listens_for(oa.node, "load")
    @listens_for(oa.way, "load")
    @listens_for(oa.relation, "load")
    def _instance_loading(target, context, _=None):
        # Get query session
        session = context.session

        # Skip if the session was in a trigger before
        # Prevents recursion in import code
        if hasattr(session, "_osmalchemy_in_trigger"):
            return

        # Determine OSM element type and id
        type_ = target.__class__.__name__[3:].lower()
        id_ = target.id


        # Guard against broken objects without an id
        if id_ is None:
            return

        oa.logger.debug("Loading instance of type %s with id %i." % (type_, id_))

        # Check whether object needs to be refreshed
        updated = target.osmalchemy_updated
        timediff = datetime.datetime.now() - updated
        if timediff.total_seconds() < oa.maxage:
            oa.logger.debug("Instance is only %i seconds old, not refreshing online." % timediff.total_seconds())
            return

        oa.logger.debug("Refreshing instance online.")

        # Get object by id as XML
        xml = _get_single_element_by_id(oa.overpass, type_, id_)

        # Import data
        session._osmalchemy_in_trigger = True
        _import_osm_xml(oa, xml, session=session)
        del session._osmalchemy_in_trigger

    @listens_for(Query, "before_compile")
    def _query_compiling(query):
        # Get the session associated with the query:
        session = query.session

        # Skip if the session was in a trigger before
        # Prevents recursion in import code
        if hasattr(session, "_osmalchemy_in_trigger"):
            return

        # Prevent recursion by skipping already-seen queries
        if query in _visited_queries:
            return
        else:
            _visited_queries.add(query)

        oa.logger.debug("Analysing new ORM query.")

        # Check whether this query affects our model
        affected_models = set([c["type"] for c in query.column_descriptions])
        our_models = set([oa.node, oa.way,  oa.relation,
                          oa.element])
        if affected_models.isdisjoint(our_models):
            # None of our models is affected
            oa.logger.debug("None of our models are affected.")
            return

        # Check whether this query filters elements
        # Online update will only run on a specified set, not all data
        if query.whereclause is None:
            # No filters
            oa.logger.debug("No filters found in query.")
            return

        oa.logger.debug("Building query tree from ORM query structure.")

        # Analyse where clause looking for all looked-up fields
        trees = {}
        for target in our_models.intersection(affected_models):
            # Build expression trees first
            tree = _where_to_tree(query.whereclause, target)
            if not tree is None:
                trees[target.__name__] = tree

        # Bail out if no relevant trees were built
        if not trees:
            oa.logger.debug("No relevant query trees built.")
            return

        # Compile to OverpassQL
        oql = _trees_to_overpassql(trees)
        oa.logger.debug("Compiled OverpassQL: %s" % oql)

        # Look up query in cache
        hashed_oql = md5(_normalise_overpassql(oql).encode()).hexdigest()
        cached_query = session.query(oa.cached_query).filter_by(oql_hash=hashed_oql).scalar()
        # Check age if cached query was found
        if cached_query:
            timediff = datetime.datetime.now() - cached_query.oql_queried
            if timediff.total_seconds() < oa.maxage:
                # Return and do nothing if query was run recently
                oa.logger.debug("Query was run online only %i seconds ago, not running." % timediff.total_seconds())
                return

        # Run query online
        oa.logger.debug("Running Overpass query.")
        xml = _get_elements_by_query(oa.overpass, oql)

        # Import data
        session._osmalchemy_in_trigger = True
        _import_osm_xml(oa, xml, session=session)
        del session._osmalchemy_in_trigger

        # Store or update query time
        if not cached_query:
            cached_query = oa.cached_query()
            cached_query.oql_hash = hashed_oql
        cached_query.oql_queried = datetime.datetime.now()
        session.add(cached_query)
        session.commit()
        oa.logger.debug("Query cached.")
