#!/usr/bin/env python3

import logging

import psycopg2 as psycopg2
import psycopg2.extras as psycopg2e
from shapely import wkb

import gv_dbconnector.attribute as gv_attribute
import gv_dbconnector.source as gv_source
import gv_dbconnector.settings as gv_settings


SELECTREQUEST = """SELECT cp.id as cp_id, ST_AsBinary(cpg.geom) as cp_geom, cpa.value as cp_att, cp.source_id as source_id
                FROM collection_point as cp
                LEFT OUTER JOIN cp_geom as cpg ON cp.id = cpg.cp_id
                LEFT OUTER JOIN cp_att as cpa ON cp.id = cpa.cp_id AND cpa.att_name = %s"""


class CollectionPoint:
    """
    Class that expose the possible interactions with the collection_point table
    Stores a copy of those collection points to prevent querying the database each minutes
    """

    def __init__(self, dbcon):
        """
        :param dbcon: connection object used all the way (class)
        """
        self.dbcon = dbcon  #: connection object used all the way (class)
        self.source = gv_source.Source(dbcon)  #: source (class)
        self.attribute = gv_attribute.Attribute(dbcon, 'cp')  #: attribute (class)
        self.collectionpoints = self.get()  #: collection points (dict{source_id: dict{cp_ids: (geom_wkt, name)}})

    def get(self, sourceid=None):
        """
        Get collection points from sourceid if provided, all if not

        :param sourceid: source id's to filter against (int)
        :return: collection points (list[dict{colname: colvalue}]) or (dict{source_id: dict{cp_ids: [geom, name]}})
        """
        if sourceid is not None:
            return self._get_from_source_id(sourceid)
        return self._get_all()

    def _get_from_source_id(self, sourceid):
        """
        Get the collection points of the given source id's

        :param sourceid: source id's to filter against (int)
        :return: collection points (list[dict{colname: colvalue}])
        """
        values = []
        sqlstr = SELECTREQUEST + " WHERE cp.source_id = %s;"
        cur = self.dbcon.cursor(cursor_factory=psycopg2e.DictCursor)
        try:
            cur.execute(sqlstr, ("name", sourceid))

            for result in cur.fetchall():
                result['cp_geom'] = wkb.loads(result.get('cp_geom').tobytes())
                values.append(result)

            self.dbcon.commit()
        except Exception as e:
            logging.error('Error while getting collection point from source id')
            if isinstance(e, psycopg2.Error):
                logging.error(str(e.pgcode) + ': ' + str(e.pgerror))
            else:
                logging.error(e)
            self.dbcon.rollback()
        finally:
            cur.close()
        return values

    def _get_all(self):
        """
        Return all the collection points from all the sources

        :return: collection points (dict{source_id: dict{cp_ids: [geom, name]}})
        """
        values = {sourceid: {} for sourceid in self.source.ids.keys()}
        sqlstr = SELECTREQUEST + ";"
        cur = self.dbcon.cursor(cursor_factory=psycopg2e.DictCursor)
        try:
            cur.execute(sqlstr, ("name", ))

            for result in cur.fetchall():
                sourceid = result.get('source_id')
                values[sourceid][result.get('cp_id')] = [wkb.loads(result.get('cp_geom').tobytes()), result.get('cp_att')]

            self.dbcon.commit()
        except Exception as e:
            logging.error('Error while getting collection points')
            if isinstance(e, psycopg2.Error):
                logging.error(str(e.pgcode) + ': ' + str(e.pgerror))
            else:
                logging.error(e)
            self.dbcon.rollback()
        finally:
            cur.close()
        return values

    def update(self, sourceid, cpid, geom):
        sqlupdate = "UPDATE cp_geom SET geom = ST_SetSRID(%s::geometry, %s) WHERE cp_id = %s;"
        cur = self.dbcon.cursor()
        try:
            cur.execute(sqlupdate, (geom.wkb_hex, gv_settings.DB_SRID, cpid,))
            self.dbcon.commit()

            name = self.collectionpoints[sourceid].get(cpid, (None, None))[1]
            self.collectionpoints[sourceid].update({cpid: [geom, name]})
        except Exception as e:
            logging.error('Error while updating collection point')
            if isinstance(e, psycopg2.Error):
                logging.error(str(e.pgcode) + ': ' + str(e.pgerror))
            else:
                logging.error(e)
            self.dbcon.rollback()
        finally:
            cur.close()

    def add(self, cpid, sourceid, geom, atts=None):
        """
        Run an insert command on collection_point and cp_geom tables
        Update local copy

        :param cpid: id of the collection point to add (string)
        :param sourceid: source id of the collection point (int)
        :param geom: geom of the collection point represented as the wkb_hex value of a LineString (geom string)
        :param atts: list of attribute (list[dict{attname: attvalue}])
        :return: None
        """
        sqlcpstr = "INSERT INTO collection_point (id, source_id) VALUES (%s, %s);"
        sqlgeomstr = "INSERT INTO cp_geom (geom, cp_id) VALUES (ST_SetSRID(%s::geometry, %s), %s);"
        cur = self.dbcon.cursor()
        try:
            cur.execute(sqlcpstr, (cpid, sourceid,))
            self.dbcon.commit()
            cur.execute(sqlgeomstr, (geom.wkb_hex, gv_settings.DB_SRID, cpid,))
            self.dbcon.commit()

            self.collectionpoints[sourceid].append(cpid)

            if atts is not None:
                self.attribute.add(atts)

        except Exception as e:
            logging.error('Error while inserting collection point')
            if isinstance(e, psycopg2.Error):
                logging.error(str(e.pgcode) + ': ' + str(e.pgerror))
            else:
                logging.error(e)
            self.dbcon.rollback()
        finally:
            cur.close()
