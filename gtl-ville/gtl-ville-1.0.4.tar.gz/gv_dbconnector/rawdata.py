#!/usr/bin/env python3

import logging

import psycopg2 as psycopg2
import psycopg2.extras as psycopg2e

import gv_dbconnector.metric as gv_metric


class RawData:
    """
    Class that expose the possible interactions with the raw_data table
    """

    def __init__(self, dbcon):
        """
        :param dbcon: connection object used all the way (class)
        """
        self.dbcon = dbcon  #: connection object used all the way (class)
        self.metric = gv_metric.Metric(dbcon)  #: metric (class)

    def add(self, data):
        """
        Run an insert command on raw_data table

        :param data: raw data to add (list[dict{colname: colvalue}])
        :return: None
        """
        sqlstr = 'INSERT INTO raw_data (timestamp, value, metric_id, cp_id) VALUES %s'
        template = '(%(timestamp)s, %(value)s, %(metric_id)s, %(cp_id)s)'
        cur = self.dbcon.cursor()
        try:
            psycopg2e.execute_values(cur, sqlstr, data, template)  # faster than a loop with multiple inserts
            self.dbcon.commit()
        except Exception as e:
            logging.error('Error while inserting raw data')
            if isinstance(e, psycopg2.Error):
                logging.error(str(e.pgcode) + ': ' + str(e.pgerror))
            else:
                logging.error(e)
            self.dbcon.rollback()
        finally:
            cur.close()
