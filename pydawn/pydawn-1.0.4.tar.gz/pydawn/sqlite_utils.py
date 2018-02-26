# coding=utf-8

import sqlite3


def sqlite_get_db(db_name):
    return sqlite3.connect(db_name)


def sqlite_excute(conn, sql):
    c = conn.cursor()
    c.execute(sql)
    conn.commit()


def sqlite_query(conn, sql):
    c = conn.cursor()
    cursor = c.execute(sql)
    for row in cursor:
        yield row


if __name__ == '__main__':
    conn = sqlite_get_db("test.db")
    # create table
    create_table_sql = '''
       CREATE TABLE IF NOT EXISTS COMPANY
       (ID INTEGER PRIMARY KEY    AUTOINCREMENT,
       url           TEXT    NOT NULL,
       url_md5       TEXT     NOT NULL
        ) ;
    '''

    sqlite_excute(conn, create_table_sql)

    insert_sql = "INSERT INTO COMPANY VALUES(NULL, 'url', 'url_md5');"
    sqlite_excute(conn, insert_sql)

    # test query
    count_query = "SELECT COUNT(*) FROM COMPANY WHERE url='url'"

    for row in sqlite_query(conn, count_query):
        print row[0]