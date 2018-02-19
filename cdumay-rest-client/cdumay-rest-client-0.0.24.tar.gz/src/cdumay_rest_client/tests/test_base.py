#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import unittest
from cdumay_rest_client.client import RESTClient
from cdumay_rest_client.exceptions import NotFound


class BaseTestCase(unittest.TestCase):
    def test_post_1(self):
        client = RESTClient(server="http://jsonplaceholder.typicode.com")
        data = client.do_request(method="GET", path="/posts/1")
        self.assertEqual(data['userId'], 1)
        self.assertEqual(data['id'], 1)

    def test_post_a(self):
        client = RESTClient(server="http://jsonplaceholder.typicode.com")
        with self.assertRaises(NotFound):
            client.do_request(method="GET", path="/posts/a")
