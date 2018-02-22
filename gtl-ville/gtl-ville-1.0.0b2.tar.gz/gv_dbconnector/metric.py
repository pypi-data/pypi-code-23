#!/usr/bin/env python3

import logging

import psycopg2 as psycopg2
import psycopg2.extras as psycopg2e


class Metric:
    """
    Class that expose the possible interactions with the metric table
    """

    def __init__(self, dbcon):
        """
        :param dbcon: connection object used all the way (class)
        """
        self.dbcon = dbcon  #: connection object used all the way (class)

    @property
    def metrics(self):
        """
        :return: the metrics (list[dict{colname: colvalue}])
        """
        return self.get()

    @property
    def ids(self):
        """
        :return: the metrics (dict{id: description})
        """
        return dict([(metric['id'], metric['description']) for metric in self.metrics])

    @property
    def descriptions(self):
        """
        :return: the metrics (dict{description: id})
        """
        return dict([(metric['description'], metric['id']) for metric in self.metrics])

    def get(self, metricid=None, description=None):
        """
        Get metric from metricid or description if provided, all if not

        :param metricid: metric id's to filter against (int)
        :param description: metric description's to filter against (string)
        :return: metric (dict{colname: colvalue}) if metricid or description or metrics (list[dict{colname: colvalue}])
        """
        if metricid is not None:
            return self._get_from_id(metricid)
        if description is not None:
            return self._get_from_description(description)
        return self._get_all()

    def _get_from_id(self, metricid):
        """
        Get metric from metricid

        :param metricid: metric id's to filter against (int)
        :return: metric (dict{attname: attvalue})
        """
        value = {}
        sqlstr = 'SELECT id, description FROM metric WHERE id = %s'
        cur = self.dbcon.cursor(cursor_factory=psycopg2e.DictCursor)
        try:
            cur.execute(sqlstr, (metricid,))

            result = cur.fetchone()
            if result is not None:
                value = result

            self.dbcon.commit()
        except Exception as e:
            logging.error('Error while getting metric from id')
            if isinstance(e, psycopg2.Error):
                logging.error(str(e.pgcode) + ': ' + str(e.pgerror))
            else:
                logging.error(e)
            self.dbcon.rollback()
        finally:
            cur.close()
        return value

    def _get_from_description(self, description):
        """
        Get metric from description

        :param description: description id's to filter against (string)
        :return: metric (dict{attname: attvalue})
        """
        value = {}
        sqlstr = 'SELECT id, description FROM metric WHERE description = %s'
        cur = self.dbcon.cursor(cursor_factory=psycopg2e.DictCursor)
        try:
            cur.execute(sqlstr, (description,))

            result = cur.fetchone()
            if result is not None:
                value = result

            self.dbcon.commit()
        except Exception as e:
            logging.error('Error while getting metric from description')
            if isinstance(e, psycopg2.Error):
                logging.error(str(e.pgcode) + ': ' + str(e.pgerror))
            else:
                logging.error(e)
            self.dbcon.rollback()
        finally:
            cur.close()
        return value

    def _get_all(self):
        """
        Get all metrics

        :return: metrics (list[dict{colname: colvalue}])
        """
        values = []
        sqlstr = 'SELECT id, description FROM metric'
        cur = self.dbcon.cursor(cursor_factory=psycopg2e.DictCursor)
        try:
            cur.execute(sqlstr)

            for result in cur.fetchall():
                values.append(result)

            self.dbcon.commit()
        except Exception as e:
            logging.error('Error while getting metrics')
            if isinstance(e, psycopg2.Error):
                logging.error(str(e.pgcode) + ': ' + str(e.pgerror))
            else:
                logging.error(e)
            self.dbcon.rollback()
        finally:
            cur.close()
        return values

    def add(self, description):
        """
        Run an insert command on metric table
        Update local copies

        :param description: metric description's (string)
        :return: None
        """
        sqlstr = 'INSERT INTO metric description VALUES (%s);'
        cur = self.dbcon.cursor()
        try:
            cur.execute(sqlstr, (description,))
            self.dbcon.commit()

            self._add_local(description)
        except Exception as e:
            logging.error('Error while inserting metrics')
            if isinstance(e, psycopg2.Error):
                logging.error(str(e.pgcode) + ': ' + str(e.pgerror))
            else:
                logging.error(e)
            self.dbcon.rollback()
        finally:
            cur.close()

    def _add_local(self, description):
        """
        Add metric to local copies

        :param description: metric description's (string)
        :return: None
        """
        metricid = self.get(description=description)
        self.metrics.append({'id': metricid, 'description': description})
        self.ids[metricid] = description
        self.descriptions[description] = metricid

    def ids_to_descriptions(self, metricids):
        """
        Return metrics descriptions' from metricids

        :param metricids: metrics ids' to filter against (list[int])
        :return: metrics descriptions' (dict{metric_id: description})
        """
        return {k: v for k, v in self.ids.items() if k in metricids}

    def descriptions_to_ids(self, descriptions):
        """
        Return metrics ids' from descriptions

        :param descriptions: metrics descriptions' to filter against (list[string])
        :return: metrics ids' (dict{description: metric_id})
        """
        return {k: v for k, v in self.descriptions.items() if k in descriptions}
