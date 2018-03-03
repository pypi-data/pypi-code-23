"""Matcher that handles large scale search.
"""

from owl.features import common as feat_common
from owl.search import common as search_common
from owl.search import simple_matchers


class LargeScaleMatcher(common.BaseMatcher):
  """Matchers that work with large scale features.

  1) 
  """
  params = None

  def __init__(self, matcher_params=None):
    self.params = matcher_params

  