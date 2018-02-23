"""Evaluation pipeline for feature matching.
"""


class MatcherEvaluator(object):
  """Class to manage evaluation of a matcher.
  """
  matcher = None

  def __init__(self):
    pass

  def vis_matching(self):
    """Visualize matching result in a webpage.
    """
    pass

  def run_eval_pipeline_local(self, config_fn):
    """Local version of the evaluation pipeline.

    It takes in database and query data and produce evaluation
    results: a data file with eval summary and a webpage showing
    matching results.

    Args:
      config_fn: evaluation config file.
    See sample_config_fn.json for an example.
    """
    pass

