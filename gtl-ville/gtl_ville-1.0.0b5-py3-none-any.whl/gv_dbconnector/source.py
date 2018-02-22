#!/usr/bin/env python3

import logging

import psycopg2 as psycopg2
import psycopg2.extras as psycopg2e


class Source:
    """
    Class that expose the possible interactions with the source table
    Stores a copy of those sources to prevent querying the database each minutes
    """

    def __init__(self, dbcon):
        """
        :param dbcon: connection object used all the way (class)
        """
        self.dbcon = dbcon  #: connection object used all the way (class)

    @property
    def sources(self):
        """
        :return: the sources (list[dict{colname: colvalue}])
        """
        return self.get()

    @property
    def ids(self):
        """
        :return: the sources (dict{id: description})
        """
        return dict([(source['id'], source['description']) for source in self.sources])

    @property
    def descriptions(self):
        """
        :return: the sources (dict{description: id})
        """
        return dict([(source['description'], source['id']) for source in self.sources])

    def get(self, sourceid=None, description=None):
        """
        Get source from sourceid or description if provided, all if not

        :param sourceid: source id's to filter against (int)
        :param description: source description's to filter against (string)
        :return: source (dict{colname: colvalue}) if sourceid or description or sources (list[dict{colname: colvalue}])
        """
        if sourceid is not None:
            return self._get_from_id(sourceid)
        if description is not None:
            return self._get_from_description(description)
        return self._get_all()

    def _get_from_id(self, sourceid):
        """
        Get source from sourceid

        :param sourceid: source id's to filter against (int)
        :return: source (dict{colname: colvalue})
        """
        value = {}
        sqlstr = 'SELECT id, description FROM source WHERE id = %s'
        cur = self.dbcon.cursor(cursor_factory=psycopg2e.DictCursor)
        try:
            cur.execute(sqlstr, (sourceid,))

            result = cur.fetchone()
            if result is not None:
                value = result

            self.dbcon.commit()
        except Exception as e:
            logging.error('Error while getting source from id')
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
        Get source from description

        :param description: description id's to filter against (string)
        :return: source (dict{colname: colvalue})
        """
        value = {}
        sqlstr = 'SELECT id, description FROM source WHERE description = %s'
        cur = self.dbcon.cursor(cursor_factory=psycopg2e.DictCursor)
        try:
            cur.execute(sqlstr, (description,))

            result = cur.fetchone()
            if result is not None:
                value = result

            self.dbcon.commit()
        except Exception as e:
            logging.error('Error while getting source from description')
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
        Get all sources

        :return: sources (list[dict{colname: colvalue}])
        """
        values = []
        sqlstr = 'SELECT id, description FROM source'
        cur = self.dbcon.cursor(cursor_factory=psycopg2e.DictCursor)
        try:
            cur.execute(sqlstr)

            for result in cur.fetchall():
                values.append(result)

            self.dbcon.commit()
        except Exception as e:
            logging.error('Error while getting sources')
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
        Run an insert command on source table
        Update local copies

        :param description: source description's (string)
        :return: None
        """
        sqlstr = 'INSERT INTO source description VALUES (%s);'
        cur = self.dbcon.cursor()
        try:
            cur.execute(sqlstr, (description,))
            self.dbcon.commit()

            self._add_local(description)
        except Exception as e:
            logging.error('Error while inserting sources')
            if isinstance(e, psycopg2.Error):
                logging.error(str(e.pgcode) + ': ' + str(e.pgerror))
            else:
                logging.error(e)
            self.dbcon.rollback()
        finally:
            cur.close()

    def _add_local(self, description):
        """
        Add source to local copies

        :param description: source description's (string)
        :return: None
        """
        metricid = self.get(description=description)
        self.sources.append({'id': metricid, 'description': description})
        self.ids[metricid] = description
        self.descriptions[description] = metricid

    def ids_to_descriptions(self, sourceids):
        """
        Return sources descriptions' from sourcesids

        :param sourceids: sources ids' to filter against (list[int])
        :return: sources descriptions' (dict{source_id: description})
        """
        return {k: v for k, v in self.ids.items() if k in sourceids}

    def descriptions_to_ids(self, descriptions):
        """
        Return sources ids' from descriptions

        :param descriptions: sources descriptions' to filter against (list[string])
        :return: sources ids' (dict{description: source_id})
        """
        return {k: v for k, v in self.descriptions.items() if k in descriptions}
