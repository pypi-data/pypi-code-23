#!/usr/bin/env python
# -*- coding: utf-8  -*-

from py4j.java_gateway import JavaGateway, GatewayParameters

class Client(object):

	def __init__(self, server_port = 25333):
		self.__server_port = server_port
		self.__gateway = JavaGateway(gateway_parameters=GatewayParameters(port = server_port))
		self.__entry_point = self.__gateway.entry_point

	def ping(self, msg):
		return self.__entry_point.ping(msg)

	def query_by_mdx(self, olap_driver, olap_url, olap_catalog, olap_mdx
		, db_driver, db_username, db_userpwd):
		return self.__entry_point.query_by_mdx(olap_driver, olap_url, olap_catalog, olap_mdx
		, db_driver, db_username, db_userpwd)