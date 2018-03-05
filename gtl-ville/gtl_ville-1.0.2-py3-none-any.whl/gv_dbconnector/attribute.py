#!/usr/bin/env python3

import logging

import psycopg2 as psycopg2
import psycopg2.extras as psycopg2e


class Attribute:
    """
    Class that expose the possible interactions with the attribute tables
    """

    def __init__(self, dbcon, parent):
        """
        :param dbcon: connection object used all the way (class)
        :param parent: suffix to represent the object holding the attributes (string)
        """
        self.dbcon = dbcon  #: connection object used all the way (class)
        self.parent = parent  #: suffix to represent the object holding the attributes (string)

    def add(self, atts):
        """
        Run an insert command on attribute tables

        :param atts: attributes to add (list[dict{attname: attvalue}])
        :return: None
        """
        sqlstr = 'INSERT INTO ' + self.parent + '_att (att_name, value, ' + self.parent + '_id) VALUES %s'
        template = '(%(att_name)s, %(value)s, %(' + self.parent + '_id)s)'
        cur = self.dbcon.cursor()
        try:
            psycopg2e.execute_values(cur, sqlstr, atts, template)  # faster than a loop with multiple inserts
            self.dbcon.commit()
        except Exception as e:
            logging.error('Error while inserting attributes')
            if isinstance(e, psycopg2.Error):
                logging.error(str(e.pgcode) + ': ' + str(e.pgerror))
            else:
                logging.error(e)
            self.dbcon.rollback()
        finally:
            cur.close()
