#!/usr/bin/env python3

import psycopg2

from gv_application.logger import GVLogger
from gv_dbconnector.collectionpoint import CollectionPoint
from gv_dbconnector.metric import Metric
from gv_dbconnector.rawdata import RawData
import gv_dbconnector.settings as gv_settings
from gv_dbconnector.source import Source


class DBConnector:
    """
    Database connector object
    Expose the possible interactions with the db
    """

    def __init__(self, dbhost, dbport, dbuser, dbpass, dbname, logfile):
        self.logger = GVLogger(parent=self.__module__, logfile=logfile)  #: logger
        self.dbcon = psycopg2.connect(host=dbhost, port=dbport, user=dbuser, password=dbpass,
                                      dbname=dbname)  #: connection object used all the way
        self.collectionpoint = CollectionPoint(self.dbcon)  #: collection points manipulator
        self.rawdata = RawData(self.dbcon)  #: raw data manipulator
        self.source = Source(self.dbcon)  #: source manipulator
        self.metric = Metric(self.dbcon)  #: metric (class)

    def get_tomtom_fcd_locations(self):
        return self.get_locations(gv_settings.TOMTOM_FCD_SOURCE)

    def get_metro_pme_locations(self):
        return self.get_locations(gv_settings.METRO_PME_SOURCE)

    def get_locations(self, sourcename):
        return self.collectionpoint.collectionpoints[self.source.descriptions[sourcename]]

    def add_tomtom_fcd_location(self, cpid, geom, attributes=None):
        self.add_location(cpid, gv_settings.TOMTOM_FCD_SOURCE, geom, attributes)

    def add_metro_pme_location(self, cpid, geom, attributes=None):
        self.add_location(cpid, gv_settings.METRO_PME_SOURCE, geom, attributes)

    def add_location(self, cpid, sourcename, geom, attributes=None):
        self.collectionpoint.add(cpid, self.source.descriptions[sourcename], geom, attributes)

    async def write_raw_data(self, data):
        """
        Add raw data to the database

        :param data: raw data to write (list[dict{colname: colvalue}])
        :return: None
        """
        self.rawdata.add(data)

    def get_sources_descriptions(self):
        """
        Get all the sources descriptions from the database

        :return: sources descriptions (dict{description: id})
        """
        return self.source.descriptions

    def get_metrics_descriptions(self):
        """
        Get all the metrics descriptions from the database

        :return: metrics descriptions (dict{description: id})
        """
        return self.metric.descriptions
