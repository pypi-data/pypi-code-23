from importlib import import_module
from tensorci.helpers.url_helper import is_valid_url
from tensorci.utils.slug import to_slug


class ConfigKey(object):
  """
  Class representation of a yaml file's key-value pair.
  Contains methods for setting the key's value, as well as validating its value.

  Basic usage:

    self.my_key = ConfigKey(value='initial value', required=True)

  """

  def __init__(self, value=None, required=False, validation='truthy', custom_validation=None):
    """
    :param str value:
      Value to set for this key
    :param bool required:
      Is this key's validation required to pass?
    :param str validation:
      String name of validation instance method (of this class) to use when 'validate' is called.
      Supported values:
        - 'truthy'
        - 'slug'
        - 'url'
        - 'mod_function'
      Default: 'truthy'
    :param custom_validation:
      Callable function used for validation. If provided, will take precedent over the 'validation' param.
    """
    self.value = value
    self.required = required
    self.validation = validation
    self.custom_validation = custom_validation

  def set_value(self, val):
    """Set the value for this key"""
    self.value = val

  def is_valid(self):
    """
    Check if this class's 'value' attribute is valid

    :returns: Whether the value is considered "valid".
    :rtype: bool
    """
    # If value isn't required and also isn't specified, it's automatically valid.
    if not self.required and not self.value:
      return True

    # If value is required but not provided, it's automatically invalid.
    if self.required and not self.value:
      return False

    # If custom validation function provided, use that for validation.
    if self.custom_validation:
      return self.custom_validation(self.value)

    # If non-supported validation string provided, fallback to 'truthy' validation.
    if not hasattr(self, self.validation):
      self.validation = 'truthy'

    # Call the supported validator.
    return getattr(self, '{}_validator'.format(self.validation))()

  # --- Validators ---

  def truthy_validator(self):
    """
    :return: Whether this class's 'value' attribute is "truthy".
    :rtype: bool
    """
    return bool(self.value)

  def slug_validator(self):
    """
    :return: Whether this class's 'value' attribute is equal to its slug counterpart.
    :rtype: bool
    """
    return self.value == to_slug(self.value)

  def url_validator(self):
    """
    :return: Whether this class's 'value' attribute is a valid url.
    :rtype: bool
    """
    return is_valid_url(self.value)

  def mod_function_validator(self):
    """
    :return:
      Whether this class's 'value' attribute is a valid function path.
      Path must follow the 'module1.module2.moduleN:function_name' format.
      Example: 'src.main:train'
    :rtype: bool
    """
    # Split the path into modules/function_name
    module_str, func_str = self.value.split(':')

    # Both components must exist
    if not module_str or not func_str:
      return False

    try:
      # Ensure the provided module actually exists and can be imported
      module = import_module(module_str)
    except KeyboardInterrupt:
      exit(0)
    except:
      return False

    # Module must actually exist and have function as attr
    if not module or not hasattr(module, func_str):
      return False

    func = getattr(module, func_str)

    # Ensure function is actually of type 'function'.
    # 'instancemethod' type is not supported as of now.
    return type(func).__name__ == 'function'