"""
This module implements the INT class, used for transient number storage and manipulation.

An INT is an integer, of any size, but limited for mySQL by the mySQL type limitations.

When using built-in arithmetic expressions, floordiv (ie //) is forced for /.  O/S ???? SHOULD THIS BE ???

On construction of an instance, any invalid value is forced to 0, to prevent further errors 
 Thus INT() can be used in place of safeint().

(note that the former .value property and .valid flag have been removed.)

Ian Howie Mackenzie - 2007, July 2017
"""


class INT(int):
    """
  simple integer handling
  """

    def __new__(self, x=0):
        """ create our (immutable) int
        force invalid x to 0
    """
        try:
            i = super().__new__(self, x)
        except:
            i = super().__new__(self, 0)
        return i

    def sql(self, quoted=True):
        """ gives sql string format, including quotes (why not..)
    """
        if quoted:
            return "'%s'" % self
        else:
            return "%s" % self

#  # force floordiv

    __truediv__ = int.__floordiv__
    __rtruediv__ = int.__rfloordiv__
    #  __itruediv__=int.__ifloordiv__

    _v_mysql_type = "int(11)"
    _v_default = 0


class SMALLINT(INT):
    _v_mysql_type = "smallint"


class TINYINT(INT):
    _v_mysql_type = "tinyint"
