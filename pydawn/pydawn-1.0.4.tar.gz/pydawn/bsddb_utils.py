# coding=utf-8
from bsddb import db


def get_db(db_filename):
    adb = db.DB()
    adb.open(db_filename, dbtype=db.DB_HASH, flags=db.DB_CREATE)
    return adb


def pop_from_db(adb):
    record = adb.cursor().first()
    if record is None:
        return None
    adb.delete(record[0])
    return record
