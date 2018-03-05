"""
This module implements the FLAG class, used for transient date storage and manipulation.

A FLAG is a boolean flag, with value "" or "Y"

(note that the python bool class cannot be subclassed, so we have to do our own thing..)

(the former .valid and .value properties have been removed)

(Ian Howie Mackenzie - April 2007, July 2017)
"""


class FLAG(int):
    """
  simple boolean handling
  """

    def __new__(self, x=False):
        """ create our (immutable) int
        force invalid x to ""
    """
        i = super().__new__(self, x and 1 or 0)
        return i

    def sql(self, quoted=True):
        """ gives sql string format, including quotes
    """
        value = "Y" if self else ""
        if quoted:
            return "'%s'" % value
        else:
            return value

    def __str__(self):
        return self and "Y" or "N"

    __repr__ = __str__

    _v_mysql_type = "char(1)"
    _v_default = ""
