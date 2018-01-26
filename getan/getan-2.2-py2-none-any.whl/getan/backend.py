# -*- coding: utf-8 -*-
#
# (c) 2008, 2009, 2010 by
#   Sascha L. Teichmann <sascha.teichmann@intevation.de>
#   Ingo Weinzierl <ingo.weinzierl@intevation.de>
# (c) 2011 Björn Ricks <bjoern.ricks@intevation.de>
#
# This is Free Software licensed unter the terms of GPLv3 or later.
# For details see LICENSE coming with the source of 'getan'.
#

import logging
import os

try:
    import sqlite3 as db
except ImportError:
    from pysqlite2 import dbapi2 as db

from getan.project import Project, Entry

DEFAULT_DATABASE = "time.db"

CREATE_TABLES = [
    """
CREATE TABLE projects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    key         VARCHAR(16) NOT NULL CONSTRAINT unique_key UNIQUE,
    description VARCHAR(256),
    active      BOOLEAN DEFAULT 1
)
""",
    """
CREATE TABLE entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER REFERENCES projects(id),
    start_time  TIMESTAMP NOT NULL,
    stop_time   TIMESTAMP NOT NULL,
    description VARCHAR(256),

    CHECK (strftime('%s', start_time) <= strftime('%s', stop_time))
)
"""
]

LOAD_ACTIVE_PROJECTS = '''
SELECT id, key, description, total
FROM projects LEFT JOIN
(SELECT
    project_id,
    sum(strftime('%s', stop_time) - strftime('%s', start_time)) AS total
    FROM entries
    GROUP BY project_id) ON project_id = id
    WHERE active
'''

LOAD_ACTIVE_PROJECT = '''
SELECT id, key, description, total
FROM projects LEFT JOIN
(SELECT
    project_id,
    sum(strftime('%s', stop_time) - strftime('%s', start_time)) AS total
    FROM entries
    GROUP BY project_id) ON project_id = id
    WHERE active and key = :project_id
'''

LOAD_PROJECT_ENTRIES = '''
SELECT
    id,
    project_id,
    start_time as "[timestamp]",
    stop_time  as "[timestamp]",
    description
FROM
    entries
WHERE
    project_id = :project_id
ORDER BY
    id
DESC
'''

LOAD_PROJECT_ENTRIES_YEAR = '''
SELECT
    id,
    project_id,
    start_time as "[timestamp]",
    stop_time  as "[timestamp]",
    'no description' AS description
FROM entries
WHERE
    project_id = :project_id AND
    (description IS NULL or length(description) = 0)
GROUP BY round(julianday(start_time))
UNION
SELECT
    id,
    project_id,
    start_time as "[timestamp]",
    stop_time  as "[timestamp]",
    description
FROM entries
WHERE
    project_id = :project_id AND
    (strftime('%Y', start_time) ) = :year AND
    description IS NOT NULL AND length(description) > 0
'''

LOAD_PROJECT_ENTRIES_WEEK = '''
SELECT
    id,
    project_id,
    start_time as "[timestamp]",
    stop_time  as "[timestamp]",
    'no description' AS description
FROM entries
WHERE
    project_id = :project_id AND
    (strftime('%Y', start_time) ) = :year AND
    (description IS NULL or length(description) = 0)
    AND (strftime('%W', start_time) = :week
    OR strftime('%W', stop_time) = :week)
GROUP BY round(julianday(start_time))
UNION
SELECT
    id,
    project_id,
    start_time as "[timestamp]",
    stop_time  as "[timestamp]",
    description
FROM entries
WHERE
    project_id = :project_id AND
    (strftime('%Y', start_time) ) = :year AND
    description IS NOT NULL AND length(description) > 0
    AND (strftime('%W', start_time) = :week
    OR strftime('%W', stop_time) = :week)
ORDER BY start_time
'''

INSERT_PROJECT_ENTRY = '''
INSERT INTO entries (project_id, start_time, stop_time, description)
VALUES(?,?,?,?)
'''

INSERT_PROJECT = '''
INSERT INTO projects (key, description, active) VALUES (?,?,1)
'''

DELETE_PROJECT_ENTRY = 'DELETE FROM entries WHERE id = %i'

MOVE_ENTRY = 'UPDATE entries SET project_id = ? WHERE id = ?'

UPDATE_ENTRY = '''
UPDATE entries
    SET description = ?, start_time = ?, stop_time = ?
    WHERE id = ?
'''

UPDATE_PROJECT = 'UPDATE projects SET key = ?, description = ? WHERE id = ?'

logger = logging.getLogger()


class InvalidProjectKeyError(Exception):
    pass


class Backend(object):

    def __init__(self, database=DEFAULT_DATABASE):
        self.database = database
        self.ensure_exists()
        self.con = db.connect(database,
                              detect_types=db.PARSE_DECLTYPES |
                              db.PARSE_COLNAMES)
        self.con.text_factory = lambda x: unicode(x, "utf-8", "ignore")

    def ensure_exists(self):
        """ Creates the database file if it does not exist. """
        if os.path.isfile(self.database):
            return

        con, cur = None, None
        try:
            con = db.connect(self.database)
            cur = con.cursor()
            try:
                for sql in CREATE_TABLES:
                    cur.execute(sql)
                con.commit()
            except:
                con.rollback()
                raise
        finally:
            if cur:
                cur.close()
            if con:
                con.close()

    def load_projects(self):
        """ Loads active projects from database and returns them as array """
        logger.debug("load active projects from database.")
        cur = None
        try:
            cur = self.con.cursor()
            cur.execute(LOAD_ACTIVE_PROJECTS)

            projects = []
            while True:
                row = cur.fetchone()

                if not row:
                    break
                # check key
                if not row[1]:
                    raise InvalidProjectKeyError("Project with id %s needs "
                                                 "a key" % row[0])
                proj = Project(self, *row)
                projects.append(proj)

            logger.info("found %i active projects." % len(projects))
            return projects

        finally:
            close(cur)

    def load_project(self, key):
        logger.debug("load active projects from database.")
        cur = None
        try:
            cur = self.con.cursor()
            cur.execute(LOAD_ACTIVE_PROJECT, {"project_id": key})
            row = cur.fetchone()
            if not row:
                raise InvalidProjectKeyError("Project with key %s not "
                                             "found." % key)
            # check key
            if not row[1]:
                raise InvalidProjectKeyError("Project with id %s needs "
                                             "a key" % row[0])
            return Project(self, *row)

        finally:
            close(cur)

    def load_entries(self, project_id, year=None, week=None):
        """ Loads all entries that belong to a specific project """
        logger.debug("load entries that belong to project %s" % project_id)
        cur = None

        if week and isinstance(week, int):
            week = "%02d" % (week)

        try:
            cur = self.con.cursor()

            if year is None and week is None:
                cur.execute(LOAD_PROJECT_ENTRIES,
                            {"project_id": project_id})
            elif week is None:
                cur.execute(LOAD_PROJECT_ENTRIES_YEAR,
                            {'project_id': project_id, 'year': str(year)})
            else:
                cur.execute(LOAD_PROJECT_ENTRIES_WEEK,
                            {'project_id': project_id,
                             'week': week,
                             'year': str(year)})

            entries = []
            while True:
                row = cur.fetchone()

                if not row:
                    break
                entries.append(Entry(*row))

            logger.debug("Found %i entries that belong to project '%i'"
                         % (len(entries), project_id))
            return entries
        finally:
            close(cur)

    def insert_project_entry(self, project, stop_time, desc):
        if project is None:
            return
        cur = None
        try:
            cur = self.con.cursor()
            cur.execute(INSERT_PROJECT_ENTRY, (
                project.id, project.start, stop_time, desc))
            self.con.commit()
            logger.debug("Added new entry '%s' of project '%s' into db"
                         % (desc, project.desc))

            project.load_entries()
        finally:
            close(cur)

    def insert_project(self, key, description):
        if key is None or description is None:
            return
        cur = None
        try:
            cur = self.con.cursor()
            cur.execute(INSERT_PROJECT, (key, description))
            self.con.commit()
            logger.debug("Added a new project '%s' into db" % description)
        finally:
            close(cur)

    def delete_entries(self, entries):
        if entries is None:
            return

        cur = None
        try:
            cur = self.con.cursor()
            for entry in entries:
                cur.execute(DELETE_PROJECT_ENTRY % entry.id)
                logger.debug("Deleted entry: %s (%d)" % (entry.desc, entry.id))
            self.con.commit()
        finally:
            close(cur)

    def move_entries(self, entries, new_project_id):
        if entries is None or new_project_id is None:
            return

        cur = None
        try:
            cur = self.con.cursor()
            for entry in entries:
                cur.execute(MOVE_ENTRY, (new_project_id, entry.id))
                logger.debug("Moved entry '%s' (id=%d) to project with id %d."
                             % (entry.desc, entry.id, new_project_id))
            self.con.commit()
        finally:
            close(cur)

    def update_entry(self, entry):
        if not entry:
            return

        cur = None
        try:
            cur = self.con.cursor()
            cur.execute(UPDATE_ENTRY, (entry.desc, entry.start,
                                       entry.end, entry.id))
            self.con.commit()
            logger.debug("Updated entry to: '%s'" % (entry))
        finally:
            close(cur)

    def update_project(self, project):
        if not project:
            return

        cur = None
        try:
            cur = self.con.cursor()
            cur.execute(
                UPDATE_PROJECT, (project.key, project.desc, project.id))
            self.con.commit()
            logger.debug("Updated project: (%d) %s %s" % (project.id,
                                                          project.key,
                                                          project.desc))
        finally:
            close(cur)


def close(cur):
    """ This function closes a database cursor if it is existing """
    if cur:
        try:
            cur.close()
        except:
            logger.warn("could not close database cursor.")

# vim:set ts=4 sw=4 si et sta sts=4 fenc=utf8:
