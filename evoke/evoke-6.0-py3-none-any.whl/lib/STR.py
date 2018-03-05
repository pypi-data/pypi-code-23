"""
This module implements the STR (STR) and TAG (TAG) classes, used for transient string storage and manipulation.

A TAG is an alphanumeric string 
- maximum size 64k characters for the entire table row... 
- typically used for  a key, or title, or single word.

For longer strings, use STR.

All values are stripped of leading and trailing whitespace.

Note that, if indexed (ie KEY), STR will be text-indexed (ie fulltext), while TAG will be field (ie standard) indexed

(Ian Howie Mackenzie - April 2007, July 2017)
"""

import re


def fixed_for_sql(text):
    "makes essential fixes for use in sql"
    return str(text).replace('\\', '\\\\').replace("'", "\\'")


class STR(str):
    """
  simple string handling
  """

    def __new__(self, value=""):
        if not (value and isinstance(value, str)):
            return str.__new__(self, "")
        else:
            return str.__new__(self, value.strip(' '))

    def sql(self, quoted=True):
        """ gives sql string format, including quotes
    """
        s = fixed_for_sql(self)
        return ("'%s'" % s) if quoted else s

    _v_default = ""
    _v_mysql_type = "mediumtext"


class TAG(STR):
    _v_mysql_type = "varchar(255)"

    def sql(self, quoted=True):
        """ gives sql string format, including quotes. limted to first 255 chars
    """
        s = fixed_for_sql(self[:255])
        return ("'%s'" % s) if quoted else s


class CHAR(STR):
    _v_mysql_type = "char(1)"

    def sql(self, quoted=True):
        """ gives sql string format, limited to first char
    """
        s = fixed_for_sql(self and self[0] or '')
        return ("'%s'" % s) if quoted else s
