"""Dimension reduction processors.
"""

import abc

import os
import cPickle as pickle

from sklearn import decomposition


class DimRedProtocol(object):
  """Ways to do dimension reduction for feature.
  """
  BINARY = 0
  PCA = 1
  INCREMENTAL_PCA = 2
  TSNE = 3


class BaseDimReducer(object):
  """Base class for dim reducer.
  """
  __metaclass__ = abc.ABCMeta

  res_dir = ""
  model_filepath = ""
  model_name = ""
  protocol = None
  model = None

  @abc.abstractmethod
  def __init__(self, res_dir):
    """Init function.

    Override to pass specific parameters.
    Set default model_fn to save.

    Args:
      res_dir: directory to save result data.
    """
    self.res_dir = res_dir
    self.model_filepath = os.path.join(self.res_dir,
                                       "{}.pkl".format(self.model_name))

  @abc.abstractmethod
  def train(self, data, get_transformed=False):
    """Perform reduction.

    Args:
      data: row major numpy array.
      save_fn: relative filename to save the model under res_dir.
      get_transform: get transformed data.
    Returns:
      transformed data if needed.
    """
    pass

  @abc.abstractmethod
  def transform(self, data):
    """Transform input data based on learned reducer.

    Args:
      data: row major data matrix.
    Returns:
      transformed data.
    """
    pass

  def save_load_model(self, model_filepath=None, to_save=True):
    """Manage model save and load from pickle.

    Args:
      model_filepath: target model file to use.
      to_save: whether to save or load model.
    """
    if model_filepath is None:
      model_filepath = self.model_filepath
    if to_save:
      with open(model_filepath, "wb") as f:
        pickle.dump(self.model, f)
        print "model {} saved to {}".format(self.model_name, model_filepath)
    else:
      with open(model_filepath, "rb") as f:
        self.model = pickle.load(f)
        print "model {} loaded from {}".format(self.model_name, model_filepath)


class PCADimReducer(BaseDimReducer):
  """Class for dimensionality reduction.
  """

  def __init__(self, res_dir, num_comp=None):
    self.protocol = DimRedProtocol.PCA
    self.model_name = "PCA"
    self.model = decomposition.PCA(num_comp)
    super(PCADimReducer, self).__init__(res_dir)

  def train(self, data, get_transformed=False):
    """Train PCA model.
    """
    transformed_data = None
    print "fitting pca to data..."
    if get_transformed:
      transformed_data = self.model.fit_transform(data)
    else:
      self.model.fit(data)
    print "pca done."
    # save pca object.
    self.save_load_model(to_save=True)
    return transformed_data

  def transform(self, data):
    """Apply pca to new data.

    Args:
      data: input data to be transfomred, numpy array.
    Returns:
      transformed data.
    """
    if self.model is None and os.path.exists(self.model_filepath):
      self.save_load_model(self.model_filepath, to_save=False)
    return self.model.transform(data)


class IncrementalPCADimReducer(BaseDimReducer):
  """Incremental PCA class.
  """

  def __init__(self, res_dir, num_comp, batch_size=None):
    self.protocol = DimRedProtocol.INCREMENTAL_PCA
    self.model_name = "Incremental PCA"
    if batch_size is None:
      batch_size = 2 * num_comp
    assert batch_size > num_comp, \
    "batch size must be larger than num components"
    self.model = decomposition.IncrementalPCA(
        n_components=num_comp, batch_size=batch_size)
    super(IncrementalPCADimReducer, self).__init__(res_dir)

  def train(self, data, get_transformed=False):
    """Train incremental PCA by feeding batch data.
    """
    transformed_data = None
    print "fitting incremental pca to data..."
    self.model.partial_fit(data)
    print "incremental pca done."
    if get_transformed:
      transformed_data = self.model.transform(data)
    # save model.
    self.save_load_model(to_save=True)
    return transformed_data

  def transform(self, data):
    """Apply incremental pca to new data.

    Args:
      data: input data to be transfomred, numpy array.
    Returns:
      transformed data.
    """
    if self.model is None and os.path.exists(self.model_filepath):
      self.save_load_model(self.model_filepath, to_save=False)
    return self.model.transform(data)
