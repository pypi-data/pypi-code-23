#!/usr/bin/env python
# -*-encoding:utf-8-*-

import sqlite3


def exe(db, sql, par=()):
    '''CREATE TABLE COMPANY
           (ID INT PRIMARY KEY     NOT NULL,
           NAME           TEXT    NOT NULL,
           AGE            INT     NOT NULL,
           ADDRESS        CHAR(50),
           SALARY         REAL);'''
    # "INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
    #   VALUES (1, 'Paul', 32, 'California', 20000.00 )"

    conn = sqlite3.connect(db)
    # print "Opened database successfully";
    conn.execute(sql, par)
    # print "Table created successfully";
    conn.close()


def read(db, sql, par=()):
    # "SELECT id, name, address, salary  from COMPANY"
    conn = sqlite3.connect(db)
    # print "Opened database successfully";
    cur = conn.execute(sql, par)
    # print "Table created successfully";
    conn.close()
    return cur
    # for row in cursor:
    #    print "ID = ", row[0]
    #    print "NAME = ", row[1]
    #    print "ADDRESS = ", row[2]
    #    print "SALARY = ", row[3], "\n"
