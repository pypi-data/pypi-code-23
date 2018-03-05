"""
This module implements the FLOAT class, used (sparingly please!) for real number storage and manipulation.

(Ian Howie Mackenzie - April 2009, July 2017)
"""


class FLOAT(float):
    """
  simple float handling
  """

    def __new__(self, x=0.0):
        """ create our (immutable) float
        force invalid x to 0
    """
        try:
            i = super().__new__(self, x)
        except:
            i = super().__new__(self, 0.0)
        return i

    def sql(self, quoted=True):
        """ gives sql string format, including quotes (why not..)
    """
        if quoted:
            return "'%s'" % self
        else:
            return "%s" % self

    _v_mysql_type = "float"
    _v_default = 0.0
