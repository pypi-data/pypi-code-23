# ~*~ coding: utf-8 ~*~
#-
# OSMAlchemy - OpenStreetMap to SQLAlchemy bridge
# Copyright (c) 2016 Dominik George <nik@naturalnet.de>
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

""" Utility code for the OSMAlchemy database OSMAlchemy. """

import operator
import xml.dom.minidom as minidom
import dateutil.parser
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList, BindParameter
from sqlalchemy.sql.annotation import AnnotatedColumn

def _import_osm_dom(oa, dom, session=None):
    """ Import a DOM tree from OSM XML into an OSMAlchemy model.

    Not called directly; used by _import_osm_xml and _import_osm_file.
    """

    # Get session
    if session is None:
        session = oa.session

    oa.logger.debug("Started import of data from DOM.")

    def _dom_attrs_to_any(xml_element, osm_element):
        if "version" in xml_element.attributes.keys():
            osm_element.version = int(xml_element.attributes["version"].value)
        if "changeset" in xml_element.attributes.keys():
            osm_element.changeset = int(xml_element.attributes["changeset"].value)
        if "user" in xml_element.attributes.keys():
            osm_element.user = xml_element.attributes["user"].value
        if "uid" in xml_element.attributes.keys():
            osm_element.uid = int(xml_element.attributes["uid"].value)
        if "visible" in xml_element.attributes.keys():
            osm_element.visible = True if xml_element.attributes["visible"].value == "true" else False
        if "timestamp" in xml_element.attributes.keys():
            osm_element.timestamp = dateutil.parser.parse(xml_element.attributes["timestamp"].value)

    def _dom_tags_to_any(xml_element, osm_element):
        # Remove all tags previously associated with element
        for key in list(osm_element.tags.keys()):
            del osm_element.tags[key]

        # Iterate over all <tag /> nodes in the DOM element
        for xml_tag in xml_element.getElementsByTagName("tag"):
            # Append data to tags
            osm_element.tags[xml_tag.attributes["k"].value] = xml_tag.attributes["v"].value

    def _dom_to_node(xml_element):
        with oa.session.no_autoflush:
            # Get mandatory node id
            id_ = int(xml_element.attributes["id"].value)
            oa.logger.debug("Importing OSM node with id %i." % id_)

            # Find object in database and create if non-existent
            node = oa.session.query(oa.node).filter_by(id=id_).scalar()
            if node is None:
                node = oa.node(id=id_)

            # Store mandatory latitude and longitude
            node.latitude = xml_element.attributes["lat"].value
            node.longitude = xml_element.attributes["lon"].value

            # Store other attributes and tags
            _dom_attrs_to_any(xml_element, node)
            _dom_tags_to_any(xml_element, node)

        # Add to session
        oa.session.add(node)
        oa.session.commit()

    def _dom_to_way(xml_element):
        with oa.session.no_autoflush:
            # Get mandatory way id
            id_ = int(xml_element.attributes["id"].value)
            oa.logger.debug("Importing OSM way with id %i." % id_)

            # Find object in database and create if non-existent
            way = oa.session.query(oa.way).filter_by(id=id_).scalar()
            if way is None:
                way = oa.way(id=id_)

            # Find all related nodes
            for node in xml_element.getElementsByTagName("nd"):
                # Get node id and find object
                ref = int(node.attributes["ref"].value)
                new_node = oa.session.query(oa.node).filter_by(id=ref).one()
                # Append to nodes in way
                way.nodes.append(new_node)

            # Store other attributes and tags
            _dom_attrs_to_any(xml_element, way)
            _dom_tags_to_any(xml_element, way)

        # Add to session
        oa.session.add(way)
        oa.session.commit()

    def _dom_to_relation(xml_element):
        with oa.session.no_autoflush:
            # Get mandatory way id
            id_ = int(xml_element.attributes["id"].value)
            oa.logger.debug("Importing OSM relation with id %i." % id_)

            # Find object in database and create if non-existent
            relation = oa.session.query(oa.relation).filter_by(id=id_).scalar()
            if relation is None:
                relation = oa.relation(id=id_)

            # Find all members
            for member in xml_element.getElementsByTagName("member"):
                # Get member attributes
                ref = int(member.attributes["ref"].value)
                type_ = member.attributes["type"].value

                if "role" in member.attributes.keys():
                    role = member.attributes["role"].value
                else:
                    role = ""
                element = oa.session.query(oa.element).filter_by(id=ref, type=type_).scalar()
                if element is None:
                    # We do not know the member yet, create a stub
                    if type_ == "node":
                        element = oa.node(id=ref)
                    elif type_ == "way":
                        element = oa.way(id=ref)
                    elif type_ == "relation":
                        element = oa.relation(id=ref)
                    # We need to commit here because element could be repeated
                    oa.session.add(element)
                    oa.session.commit()
                # Append to members
                relation.members.append((element, role))

            # Store other attributes and tags
            _dom_attrs_to_any(xml_element, relation)
            _dom_tags_to_any(xml_element, relation)

        # Add to session
        oa.session.add(relation)
        oa.session.commit()

    # Get root element
    osm = dom.documentElement

    # Iterate over children to find nodes, ways and relations
    for xml_element in osm.childNodes:
        # Determine element type
        if xml_element.nodeName == "node":
            _dom_to_node(xml_element)
        elif xml_element.nodeName == "way":
            _dom_to_way(xml_element)
        elif xml_element.nodeName == "relation":
            _dom_to_relation(xml_element)

        # Rmove children
        xml_element.unlink()

def _import_osm_xml(oa, xml, session=None):
    """ Import a string in OSM XML format into an OSMAlchemy model.

      oa - reference to the OSMAlchemy model instance
      xml - string containing the XML data
    """

    # Get session
    if session is None:
        session = oa.session

    # Parse string into DOM structure
    dom = minidom.parseString(xml)

    return _import_osm_dom(oa, dom, session=session)

def _import_osm_file(oa, file, session=None):
    """ Import a file in OSM XML format into an OSMAlchemy model.

      oa - reference to the OSMAlchemy model instance
      file - path to the file to import or open file object
    """

    # Get session
    if session is None:
        session = oa.session

    # Parse file
    if isinstance(file, str):
        with open(file, "r", encoding="utf-8") as f:
            dom = minidom.parse(f)
    else:
        dom = minidom.parse(file)

    return _import_osm_dom(oa, dom, session=session)
