import os
import yaml
from collections import OrderedDict
from config_key import ConfigKey
from tensorci import log


class ConfigFile(object):
  """
  Serves as an interface to the .tensorci.yml config file.
  Contains methods to read/write the config file to disk, as well as validate its contents.

  Basic usage:

    config = ConfigFile()

  Or load the file immediately in a chained manner:

    config = ConfigFile().load()

  """
  FILE_NAME = '.tensorci.yml'

  def __init__(self, path=None, model=None, prepro_data=None, train=None,
               test=None, predict=None, reload_model=None):
    """
    The initialization params represent the keys of the config file:

    :param str path: Absolute path to the config file
    :param str model: Relative path to where the model file (or directory) lives or will live
    :param str prepro_data: Function path that preprocesses the raw dataset before training
    :param str train: Function path that trains the model
    :param str test: Function path that tests/evaluates the trained model
    :param str predict: Function path that makes a prediction with the trained model
    :param str reload_model:
      Function path that reloads the trained model from disk when an old model is swapped out
      with a newly trained model.
    """
    # Config file path
    self.path = path or '{}/{}'.format(os.getcwd(), self.FILE_NAME)

    # Establish attributes for each config file key (represented as the ConfigKey class).
    self.model = ConfigKey(value=model, required=True, custom_validation=self.model_path_validation)
    self.prepro_data = ConfigKey(value=prepro_data, required=True, validation='mod_function')
    self.train = ConfigKey(value=train, required=True, validation='mod_function')
    self.test = ConfigKey(value=test, required=False, validation='mod_function')
    self.predict = ConfigKey(value=predict, required=True, validation='mod_function')
    self.reload_model = ConfigKey(value=reload_model, required=False, validation='mod_function')

    self.config = dict(model=self.model,
                       prepro_data=self.prepro_data,
                       train=self.train,
                       test=self.test,
                       predict=self.predict,
                       reload_model=self.reload_model)

  def as_ordered_dict(self):
    """
    Creates an ordered dict from the config's key-val pairs.

    :return: 'OrderedDict' of config's key-val pairs.
    :rtype: collections.OrderedDict
    """
    d = OrderedDict()

    # Add keys in the order we want them
    d['model'] = self.model.value
    d['prepro_data'] = self.prepro_data.value
    d['train'] = self.train.value
    d['test'] = self.test.value
    d['predict'] = self.predict.value
    d['reload_model'] = self.reload_model.value

    return d

  def load(self):
    """
    Load the config file from disk, and for each key-val pair,
    assign the value to this class's key attribute counterpart.

    Ex:
      'model: data/model.ckpt' (in config file) would result in
      self.model.value = 'data/model.ckpt'

    :return: self
    """
    # Return early if config file doesn't even exist yet
    if not os.path.exists(self.path):
      return self

    # Load the yaml config file from disk
    with open(self.path, 'r') as f:
      file_config = yaml.load(f)

    # For each key-val pair, assign the value to this class's key attribute counterpart.
    for k, v in file_config.items():
      self.set_value(k, v)

    return self

  def set_value(self, key, val):
    """Store a key-val pair on this class"""
    if key in self.config:
      self.config[key].set_value(val)

  def save(self):
    """Write this class's key-val pairs to disk inside the config file"""
    with open(self.path, 'w+') as f:
      yaml.dump(self.as_ordered_dict(), f, default_flow_style=False)

  def is_valid(self):
    """
    Validate each of the config file's key-val pairs

    :return: Whether the config file is valid or not
    :rtype: bool
    """
    # File has to exist in order to be valid...
    if not os.path.exists(self.path):
      log('A {} config file must exist before running this command.\n'.format(self.FILE_NAME) +
          'Run \'tensorci init\' to initialize your project and create this file.')
      return False

    # Find which keys are invalid
    invalid_keys = []
    for k, v in self.config.items():
      if not v.is_valid():
        invalid_keys.append(k)

    # Tell the user which keys were invalid
    if invalid_keys:
      log('Invalid config keys: {}'.format(', '.join(invalid_keys)))

    return len(invalid_keys) == 0

  def abs_model_path(self):
    """
    Construct an absolute path from the specified 'model' key's relative path

    returns: model's would-be absolute path
    :rtype: str
    """
    return os.path.join(os.getcwd(), self.model.value)

  @staticmethod
  def model_path_validation(val):
    """
    Custom validation method for the 'model' key

    :return: If the 'model' key is valid
    :rtype: bool
    """
    # Ensure model path is a relative path
    return bool(val) and not val.startswith('/')


def setup_yaml():
  """Allow yaml library to save our data as an ordered dict"""
  represent_dict_order = lambda self, data: self.represent_mapping('tag:yaml.org,2002:map', data.items())
  yaml.add_representer(OrderedDict, represent_dict_order)


setup_yaml()