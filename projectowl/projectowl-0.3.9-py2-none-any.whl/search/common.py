"""Shared definition for matcher.
"""

import abc


class MatcherType(object):
  """Built-in matcher type.
  """
  L2 = 0
  L1 = 1
  HAMMING = 2
  ANGULAR = 3


class MatchProtocol(object):
  """How to conduct match.
  """
  EXACT = 0
  APPROXIMATE = 1


class MatcherParams(object):
  """Parameters for matcher.
  """
  matcher_type = MatcherType.L2
  matcher_protocol = MatchProtocol.APPROXIMATE


class BaseMatcher(object):
  """Base class for a matcher.

  A matcher computes matches a set of queries to a database and
  return a ranked list of the item.
  """
  __metaclass__ = abc.ABCMeta

  matcher_type = None
  matcher_name = ""
  match_protocol = MatchProtocol.EXACT
  res_dir = None

  @abc.abstractmethod
  def __init__(self, name, matcher_type, res_dir=None):
    self.matcher_name = name
    self.res_dir = res_dir
    self.matcher_type = matcher_type

  @abc.abstractmethod
  def prepare_database(self, db_items):
    """Load database items.

    Args:
      db_items: database items, can take any form based
      on custom implementation.
    """
    pass

  @abc.abstractmethod
  def match(self, query_items, top_nn=10, dist_func=None):
    """Perform match on the database for each query.

    Args:
      query_items: a set of query image data. Can take any form.
      top_nn: top results to return.
      dist_func: custom distance function.
    Returns:
      ranked list of db items for each query.
    """
    pass
