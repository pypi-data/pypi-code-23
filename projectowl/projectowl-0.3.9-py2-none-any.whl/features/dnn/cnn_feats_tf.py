"""CNN feature extractor from tensorflow models.
"""

from owl.features import common

from deepmodels.tf.core import commons
from deepmodels.tf.core.dm_models import dm_model_factory
from deepmodels.tf.core.learners import dm_classifier


class CNNFeatParams(common.BaseFeatParams):
  """Parameters for CNN features.
  """
  pass


class CNNFeatExtractor(common.BaseFeatExtractor):
  """CNN feature extractor.
  """

  network = None
  network_params = None

  def start(self):
    """Prepare deep models.
    """
    network = dm_model_factory.get_dm_model(commons.ModelType.INCEPTION_V4)
    learner = dm_classifier.DMClassifier()
