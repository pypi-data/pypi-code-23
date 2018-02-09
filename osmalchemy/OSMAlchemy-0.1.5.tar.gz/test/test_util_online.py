#!/usr/bin/env python3
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

""" Tests concerning OSMAlchemy online utility code. """

# Standard unit testing framework
import unittest

class OSMAlchemyUtilOnlineSQLToOverpassQLTests(unittest.TestCase):
    """ Tests for SQL to overpass conversion """

    def test_trees_to_overpassql_bbox_node(self):
        # Import function to test
        from osmalchemy.util.online import _trees_to_overpassql

        # Test input
        tree = {"OSMNode": ("&&", [(">", "latitude", 51.0), ("<", "latitude", 52.0),
                                   (">", "longitude", 7.0), ("<", "longitude", 8.0)])}

        # Expected result regex
        expected = r"^node\(51\.0000000,7\.0000000,52\.0000000,8\.0000000\)->\.s[0-9]+;\(\.s[0-9]+;\);$"

        # Run transformation
        res = _trees_to_overpassql(tree)

        # Check result
        self.assertRegexpMatches(res, expected)

    def test_trees_to_overpassql_bbox_node_le_ge(self):
        # Import function to test
        from osmalchemy.util.online import _trees_to_overpassql

        # Test input
        tree = {"OSMNode": ("&&", [(">=", "latitude", 51.0), ("<=", "latitude", 52.0),
                                   (">=", "longitude", 7.0), ("<=", "longitude", 8.0)])}

        # Expected result regex
        expected = r"^node\(51\.0000000,7\.0000000,52\.0000000,8\.0000000\)->\.s[0-9]+;\(\.s[0-9]+;\);$"

        # Run transformation
        res = _trees_to_overpassql(tree)

        # Check result
        self.assertRegexpMatches(res, expected)

    def test_trees_to_overpassql_bbox_node_missing_east(self):
        # Import function to test
        from osmalchemy.util.online import _trees_to_overpassql

        # Test input
        tree = {"OSMNode": ("&&", [(">", "latitude", 51.0), ("<", "latitude", 52.0),
                                   (">", "longitude", 7.0)])}

        # Expected result regex
        expected = r"^node\(51\.0000000,7\.0000000,52\.0000000,180\.0000000\)->\.s[0-9]+;\(\.s[0-9]+;\);$"

        # Run transformation
        res = _trees_to_overpassql(tree)

        # Check result
        self.assertRegexpMatches(res, expected)

    def test_trees_to_overpassql_bbox_node_missing_west(self):
        # Import function to test
        from osmalchemy.util.online import _trees_to_overpassql

        # Test input
        tree = {"OSMNode": ("&&", [(">", "latitude", 51.0), ("<", "latitude", 52.0),
                                   ("<", "longitude", 8.0)])}

        # Expected result regex
        expected = r"^node\(51\.0000000,-180\.0000000,52\.0000000,8\.0000000\)->\.s[0-9]+;\(\.s[0-9]+;\);$"

        # Run transformation
        res = _trees_to_overpassql(tree)

        # Check result
        self.assertRegexpMatches(res, expected)

    def test_trees_to_overpassql_bbox_node_missing_north(self):
        # Import function to test
        from osmalchemy.util.online import _trees_to_overpassql

        # Test input
        tree = {"OSMNode": ("&&", [(">", "latitude", 51.0),
                                   (">", "longitude", 7.0), ("<", "longitude", 8.0)])}

        # Expected result regex
        expected = r"^node\(51\.0000000,7\.0000000,90\.0000000,8\.0000000\)->\.s[0-9]+;\(\.s[0-9]+;\);$"

        # Run transformation
        res = _trees_to_overpassql(tree)

        # Check result
        self.assertRegexpMatches(res, expected)

    def test_trees_to_overpassql_bbox_node_missing_south(self):
        # Import function to test
        from osmalchemy.util.online import _trees_to_overpassql

        # Test input
        tree = {"OSMNode": ("&&", [("<", "latitude", 52.0),
                                   (">", "longitude", 7.0), ("<", "longitude", 8.0)])}

        # Expected result regex
        expected = r"^node\(-90\.0000000,7\.0000000,52\.0000000,8\.0000000\)->\.s[0-9]+;\(\.s[0-9]+;\);$"

        # Run transformation
        res = _trees_to_overpassql(tree)

        # Check result
        self.assertRegexpMatches(res, expected)

    def test_trees_to_overpassql_id_node(self):
        # Import function to test
        from osmalchemy.util.online import _trees_to_overpassql

        # Test input
        tree = {"OSMNode": ("==", "id", 1145698)}

        # Expected result regex
        expected = r"^node\(1145698\)->\.s[0-9]+;\(\.s[0-9]+;\);$"

        # Run transformation
        res = _trees_to_overpassql(tree)

        # Check result
        self.assertRegexpMatches(res, expected)

    def test_trees_to_overpassql_id_node_invalid(self):
        # Import function to test
        from osmalchemy.util.online import _trees_to_overpassql

        # Test input
        tree = {"OSMNode": (">", "id", 1145698)}

        # Expect it to throw an exception
        with self.assertRaises(ValueError):
            # Run transformation
            res = _trees_to_overpassql(tree)

    def test_trees_to_overpassql_two_tags_node(self):
        # Import function to test
        from osmalchemy.util.online import _trees_to_overpassql

        # Test input
        tree = {"OSMNode": ("&&", [("==", "amenity", "pub"), ("==", "name", "Bruchbude")])}

        # Expected result regex
        expected = r"^node\[\"amenity\"=\"pub\"\]\[\"name\"=\"Bruchbude\"\]->\.s[0-9]+;\(\.s[0-9]+;\);$"

        # Run transformation
        res = _trees_to_overpassql(tree)

        # Check result
        self.assertRegexpMatches(res, expected)

    def test_trees_to_overpassql_any_of_two_tags_node(self):
        # Import function to test
        from osmalchemy.util.online import _trees_to_overpassql

        # Test input
        tree = {"OSMNode": ("||", [("==", "amenity", "pub"), ("==", "name", "Bruchbude")])}

        # Expected result regex
        expected = r"^node\[\"amenity\"=\"pub\"\]->\.s[0-9]+;node\[\"name\"=\"Bruchbude\"\]->\.s[0-9]+;\(\.s[0-9]+;\.s[0-9]+;\)->\.s[0-9]+;\(\.s[0-9]+;\);$"

        # Run transformation
        res = _trees_to_overpassql(tree)

        # Check result
        self.assertRegexpMatches(res, expected)

    def test_trees_to_overpassql_two_tags_in_bbox_node(self):
        # Import function to test
        from osmalchemy.util.online import _trees_to_overpassql

        # Test input
        tree = {"OSMNode": ("&&", [("==", "amenity", "pub"), ("==", "name", "Bruchbude"),
                                   (">", "latitude", 51.0), ("<", "latitude", 52.0),
                                   (">", "longitude", 7.0), ("<", "longitude", 8.0)])}

        # Expected result regex
        expected = r"^node\[\"amenity\"=\"pub\"\]\[\"name\"=\"Bruchbude\"\]\(51\.0000000,7\.0000000,52\.0000000,8\.0000000\)->\.s[0-9]+;\(\.s[0-9]+;\);$"

        # Run transformation
        res = _trees_to_overpassql(tree)

        # Check result
        self.assertRegexpMatches(res, expected)

    def test_normalise_overpassql(self):
        # Import function to test
        from osmalchemy.util.online import _normalise_overpassql

        # Test string
        oql = 'node(50.0,6.0,51.0,8.0)->.s1875312;node["name"="Schwarzreindorf Kirche"]->.s95682773;(.s1875312; .s95682773)->.s173859;.s173859 out meta;'

        # Expected result
        normalised_oql = 'node(50.0,6.0,51.0,8.0)->.s;node["name"="Schwarzreindorf Kirche"]->.s;(.s; .s)->.s;.s out meta;'

        # Run function
        res = _normalise_overpassql(oql)

        # Check result
        self.assertEqual(res, normalised_oql)

    def test_normalise_overpassql_with_catchy_string(self):
        # Import function to test
        from osmalchemy.util.online import _normalise_overpassql

        # Test string
        oql = 'node(50.0,6.0,51.0,8.0)->.s1875312;node["name"="Whatever.s192837465"]->.s95682773;(.s1875312; .s95682773)->.s173859;.s173859 out meta;'

        # Expected result
        normalised_oql = 'node(50.0,6.0,51.0,8.0)->.s;node["name"="Whatever.s192837465"]->.s;(.s; .s)->.s;.s out meta;'

        # Run function
        res = _normalise_overpassql(oql)

        # Check result
        self.assertEqual(res, normalised_oql)

    def test_escape_tag_nothing(self):
        # Import function to test
        from osmalchemy.util.online import _escape_tag

        # Test string
        tag = "foobar"

        # Expected result
        escaped_tag = "foobar"

        # Run function
        res = _escape_tag(tag)

        # Check result
        self.assertEqual(res, escaped_tag)

    def test_escape_tag_quote(self):
        # Import function to test
        from osmalchemy.util.online import _escape_tag

        # Test string
        tag = "foo\"bar"

        # Expected result
        escaped_tag = "foo\\\"bar"

        # Run function
        res = _escape_tag(tag)

        # Check result
        self.assertEqual(res, escaped_tag)

    def test_escape_tag_backslash(self):
        # Import function to test
        from osmalchemy.util.online import _escape_tag

        # Test string
        tag = "foo\\bar"

        # Expected result
        escaped_tag = "foo\\\\bar"

        # Run function
        res = _escape_tag(tag)

        # Check result
        self.assertEqual(res, escaped_tag)

    def test_escape_tag_quote_backslash(self):
        # Import function to test
        from osmalchemy.util.online import _escape_tag

        # Test string
        tag = "foo\\\"bar"

        # Expected result
        escaped_tag = "foo\\\\\\\"bar"

        # Run function
        res = _escape_tag(tag)

        # Check result
        self.assertEqual(res, escaped_tag)

# Make runnable as standalone script
if __name__ == "__main__":
    unittest.main()
