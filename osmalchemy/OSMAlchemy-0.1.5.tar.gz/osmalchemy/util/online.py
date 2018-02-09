## ~*~ coding: utf-8 ~*~
#-
# OSMAlchemy - OpenStreetMap to SQLAlchemy bridge
# Copyright (c) 2016, 2017 Dominik George <nik@naturalnet.de>
# Copyright (c) 2016 Eike Tim Jesinghaus <eike@naturalnet.de>
# Copyright (c) 2017 mirabilos <thorsten.glaser@teckids.org>
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

""" Utility code for OSMAlchemy's overpass code. """

import operator
import overpass
import re
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList, BindParameter, Grouping
from sqlalchemy.sql.annotation import AnnotatedColumn
from sqlalchemy.sql.selectable import Exists

def _generate_overpass_api(endpoint=None):
    """ Create and initialise the Overpass API object.

    Passing the endpoint argument will override the default
    endpoint URL.
    """

    # Create API object with default settings
    api = overpass.API()

    # Change endpoint if desired
    if not endpoint is None:
        api.endpoint = endpoint

    return api

def _get_single_element_by_id(api, type_, id_, recurse_down=True):
    """ Retrieves a single OpenStreetMap element by its id.

      api - an initialised Overpass API object
      type_ - the element type to query, one of node, way or relation
      id_ - the id of the element to retrieve
      recurse_down - whether to get child nodes of ways and relations
    """

    # Construct query
    query = "%s(%d);%s" % (type_, id_, "(._;>;);" if recurse_down else "")

    # Run query
    result = api.Get(query, responseformat="xml")

    # Return data
    return result

def _get_elements_by_query(api, query, recurse_down=True):
    """ Runs a query and returns the resulting OSM XML.

      api - an initialised Overpass API object
      query - the OverpassQL query
      recurse_down - whether to get child nodes of ways and relations
    """

    # Run query
    result = api.Get("%s%s" % (query, "(._;>;);" if recurse_down else ""), responseformat="xml")

    # Return data
    return result

# Define operator to string mapping
_OPS = {operator.eq: "==",
        operator.ne: "!=",
        operator.lt: "<",
        operator.gt: ">",
        operator.le: "<=",
        operator.ge: ">=",
        operator.and_: "&&",
        operator.or_: "||"}

def _where_to_tree(clause, target):
    """ Transform an SQLAlchemy whereclause to an expression tree.

    This function analyses a Query.whereclause object and turns it
    into a more general data structure.
    """

    if isinstance(clause, BinaryExpression):
        # This is something like "latitude >= 51.0"
        left = clause.left
        right = clause.right
        op = clause.operator

        # Left part should be a column
        if isinstance(left, AnnotatedColumn):
            # Get table class and field
            model = left._annotations["parentmapper"].class_
            field = left

            # Only use if we are looking for this model
            if model is target:
                # Store field name
                left = field.name
            else:
                return None
        else:
            # Right now, we cannot cope with anything but a column on the left
            return None

        # Right part should be a literal value
        if isinstance(right, BindParameter):
            # Extract literal value
            right = right.value
        else:
            # Right now, we cannot cope with something else here
            return None

        # Look for a known operator
        if op in _OPS.keys():
            # Get string representation
            op = _OPS[op]
        else:
            # Right now, we cannot cope with other operators
            return None

        # Return polish notation tuple of this clause
        return (op, left, right)

    elif isinstance(clause, BooleanClauseList):
        # This is an AND or OR operation
        op = clause.operator
        clauses = []

        # Iterate over all the clauses in this operation
        for clause in clause.clauses:
            # Recursively analyse clauses
            res = _where_to_tree(clause, target)
            # None is returned for unsupported clauses or operations
            if res is not None:
                # Append polish notation result to clauses list
                clauses.append(res)

        # Look for a known operator
        if op in _OPS.keys():
            # Get string representation
            op = _OPS[op]
        else:
            # Right now, we cannot cope with anything else
            return None

        # Return polish notation tuple of this clause
        return (op, clauses)

    elif isinstance(clause, Exists):
        # This case is a bit hard to verify.
        # We expect this to be the EXISTS sub-clause of something like:
        #
        #  session.query(osmalchemy.node).filter(
        #   osmalchemy.node.tags.any(key="name", value="Schwarzrheindorf Kirche")
        #  ).all()
        #
        # For now, we stick with simply expecting that until someone
        # rewrites this entire code.
        try:
            # Try to get the real conditionals from this weird statement
            conditionals = (clause.get_children()[0]._whereclause.clauses[1].
                get_children()[0].get_children()[0]._whereclause.clauses[1].clauses)
        except:
            # Simply return None if we got something unexpected
            return None

        key = ""
        value = ""

        for clause in conditionals:
            if clause.left.name == "key":
                key = clause.right.value
            elif clause.left.name == "value":
                value = clause.right.value

        # Check if we got only a key, a key and a value or neither
        if key and not value:
            return ("has", key, "")
        elif key and value:
            return ("==", key, value)
        else:
            return None

    elif isinstance(clause, Grouping):
        # Ungroup by simply taking the first element of the group
        # This is not correct in general, but correct for all documented
        # use cases.
        return _where_to_tree(clause.get_children()[0], target)

    else:
        # We hit an unsupported type of clause
        return None

def _trees_to_overpassql(tree_dict):
    """ Transform an expression tree (from _where_to_tree) into OverpassQL. """

    # Called recursively on all subtrees
    def _tree_to_overpassql_recursive(tree, type_):
        # Empty result string
        result = ""

        # Test if we got a tree or an atom
        if isinstance(tree[1], list):
            # We are in a subtree

            # Store operation of subtree (conjunction/disjunction)
            op = tree[0]

            # Empty bounding box
            bbox = [None, None, None, None]

            # List of genrated set names
            set_names = []

            # Iterate over all elements in the conjunction/disjunction
            for element in tree[1]:
                # Check if element is a tree or an atom
                if isinstance(element[1], list):
                    # Recurse into inner tree
                    result_inner_tree = _tree_to_overpassql_recursive(tree[1])
                    # Store resulting query and its name
                    result += "%s" % result_inner_tree[1]
                    set_names.append(result_inner_tree[0])
                else:
                    # Parse atom

                    # latitude and longitude comparisons form a bounding box
                    if element[1] == "latitude" and element[0] in [">", ">="]:
                        # South edge
                        if bbox[0] is None:
                            bbox[0] = float(element[2])
                        elif op == "&&" and bbox[0] <= element[2]:
                            bbox[0] = float(element[2])
                        elif op == "||" and bbox[0] >= element[2]:
                            bbox[0] = float(element[2])
                    elif element[1] == "latitude" and element[0] in ["<", "<="]:
                        # North edge
                        if bbox[2] is None:
                            bbox[2] = float(element[2])
                        elif op == "&&" and bbox[2] >= element[2]:
                            bbox[2] = float(element[2])
                        elif op == "||" and bbox[2] <= element[2]:
                            bbox[2] = float(element[2])
                    elif element[1] == "longitude" and element[0] in [">", ">="]:
                        # West edge
                        if bbox[1] is None:
                            bbox[1] = float(element[2])
                        elif op == "&&" and bbox[1] <= element[2]:
                            bbox[1] = float(element[2])
                        elif op == "||" and bbox[1] >= element[2]:
                            bbox[1] = float(element[2])
                    elif element[1] == "longitude" and element[0] in ["<", "<="]:
                        # East edge
                        if bbox[3] is None:
                            bbox[3] = float(element[2])
                        elif op == "&&" and bbox[3] >= element[2]:
                            bbox[3] = float(element[2])
                        elif op == "||" and bbox[3] <= element[2]:
                            bbox[3] = float(element[2])
                    # Query for an element with specific id
                    elif element[1] == "id" and element[0] == "==":
                        # Build query
                        if op == "||":
                            idquery = "%s(%i)" % (type_, element[2])
                            # Store resulting query and its name
                            set_name = "s%i" % id(idquery)
                            result += "%s->.%s;" % (idquery, set_name)
                            set_names.append(set_name)
                        elif op == "&&":
                            idquery = "(%i)" % (element[2])
                            # Store resulting query and its name
                            set_name = "s%i" % id(idquery)
                            result += idquery
                            set_names.append(set_name)
                    elif element[1] == "id":
                        # We got an id query, but not with equality comparison
                        raise ValueError("id can only be queried with equality")
                    # Everything else must be a tag query
                    else:
                        # Check whether it is a comparison or a query for existence
                        if element[0] == "==":
                            # Build query for tag comparison
                            if op == "||":
                                tagquery = "%s[\"%s\"=\"%s\"]" % (type_, _escape_tag(element[1]), _escape_tag(element[2]))
                            elif op == "&&":
                                tagquery = "[\"%s\"=\"%s\"]" % (_escape_tag(element[1]), _escape_tag(element[2]))
                        elif element[0] == "has":
                            if op == "||":
                                tagquery = "%s[\"%s\"]" % (type_, _escape_tag(element[1]))
                            elif op == "&&":
                                tagquery = "[\"%s\"]" % (_escape_tag(element[1]))

                        # Store resulting query and its name
                        set_name = "s%i" % id(tagquery)
                        if op == "||":
                            result += "%s->.%s;" % (tagquery, set_name)
                        elif op == "&&":
                            result += tagquery
                        set_names.append(set_name)

            # Check if any component of the bounding box was set
            if bbox != [None, None, None, None]:
                # Amend minima/maxima
                if bbox[0] is None:
                    bbox[0] = -90.0
                if bbox[1] is None:
                    bbox[1] = -180.0
                if bbox[2] is None:
                    bbox[2] = 90.0
                if bbox[3] is None:
                    bbox[3] = 180.0

                # Build query
                if op == "||":
                    bboxquery = "%s(%.7f,%.7f,%.7f,%.7f)" % (type_, bbox[0], bbox[1], bbox[2], bbox[3])
                elif op == "&&":
                    bboxquery = "(%.7f,%.7f,%.7f,%.7f)" % (bbox[0], bbox[1], bbox[2], bbox[3])
                # Store resulting query and its name
                set_name = "s%i" % id(bboxquery)
                if op == "||":
                    result += "%s->.%s;" % (bboxquery, set_name)
                elif op == "&&":
                    result += bboxquery
                set_names.append(set_name)

            # Build conjunction or disjunction according to current operation
            if len(set_names) > 1:
                if op == "&&":
                    # Conjunction, build an intersection
                    result = "%s%s" % (type_, result)
                elif op == "||":
                    # Disjunction, build a union
                    result += "("
                    for set_name in set_names:
                        result += ".%s;" % set_name
                    result += ")"
            else:
                if op == "||":
                    result += "(.%s;)" % set_names[0]
                elif op == "&&":
                    result = "%s%s" % (type_, result)
        else:
            # We got a bare atom

            # latitude and longitude are components of a bounding box query
            if tree[1] == "latitude" and tree[0] == ">":
                # South edge
                result = "%s(%.7f,-180.0,90.0,180.0)" % (type_, float(tree[2]))
            elif tree[1] == "latitude" and tree[0] == "<":
                # West edge
                result = "%s(-90.0,-180.0,%.7f,180.0)" % (type_, float(tree[2]))
            elif tree[1] == "longitude" and tree[0] == ">":
                # North edge
                result = "%s(-90.0,%.7f,-90.0,180.0)" % (type_, float(tree[2]))
            elif tree[1] == "longitude" and tree[0] == "<":
                # East edge
                result = "%s(-90.0,-180.0,-90.0,%.7f)" % (type_, float(tree[2]))
            # Query for an id
            elif tree[1] == "id" and tree[0] == "==":
                result = "%s(%i)" % (type_, tree[2])
            elif tree[1] == "id":
                # We got an id query, but not with equality comparison
                raise ValueError("id can only be queried with equality")
            # Everything else must be a tag query
            else:
                result = "%s[\"%s\"=\"%s\"]" % (type_, _escape_tag(tree[1]), _escape_tag(tree[2]))

        # generate a name for the complete set and return it, along with the query
        set_name = id(result)
        result += "->.s%i;" % set_name
        return (set_name, result)

    # Run tree transformation for each type in the input tree
    results = []
    for type_ in tree_dict.keys():
        # Get real type name (OSMNode→node,…)
        real_type = type_[3:].lower()
        # Do transformation and store query and name
        results.append(_tree_to_overpassql_recursive(tree_dict[type_], real_type))

    # Build finally resulting query in a union
    full_result = ""
    set_names = "("
    for result in results:
        full_result += result[1]
        set_names += ".s%s; " % result[0]
    set_names = "%s);" % set_names.strip()
    full_result += set_names

    # Return final query
    return full_result

def _normalise_overpassql(oql):
    """ Normalise an OverpassQL expression.

    Takes an OverpassQL string as argument and strips all set names of the form \.s[0-9]+
    """

    def replace_setname(match):
        if not match.group().startswith('"'):
            return re.sub(r"\.s[0-9]+", ".s", match.group())
        else:
            return match.group()

    return re.sub(r'"[^"]*"|([^"]*)', replace_setname, oql)

def _escape_tag(tag):
    """ Escapes special characters in a tag query component. """

    res = tag

    res = res.replace('\\', '\\\\')
    res = res.replace('"', '\\"')

    return res
