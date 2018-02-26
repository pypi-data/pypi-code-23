import logging
import yaml
from . import passwords

#==============================================
class PasswordsYAML(passwords.Passwords):

  def load(self):
    self.load_ok = False
    content = self._decryptSource()
    try:
      self.data = yaml.safe_load( content )
    except yaml.YAMLError as e:
      logging.error("Source is not valid YAML.")
      logging.error(e)
      self.data = {}
      self.load_ok = False
      return
    try:
      self._recipients = self.data.pop('RECIPIENTS')
    except KeyError as e:
      logging.warning("No RECIPIENTS list in this source.")
    try:
      self._description = self.data.pop('DESCRIPTION')
    except KeyError as e:
      logging.warning("No DESCRIPTION available for this file.")

    self.load_ok = True

