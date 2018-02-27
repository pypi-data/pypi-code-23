import os
import logging
import gnupg

#=========================================================
# Base class for a simple readonly password manager
class Passwords(object):

  def __init__(self, source, autoload=True):
    self.source = source
    self.data = {}
    self._recipients = []
    self._description = ''
    self.gpg = gnupg.GPG()
    self._source_is_encrypted = False
    self.load_ok = False
    if autoload:
      self.load()


  def _decryptSource(self):
    '''
    Get the source as a decrypted string

    :return: string
    '''
    data = None
    with open(self.source, 'rb') as input_file:
      data = self.gpg.decrypt_file(input_file)
      if data.fingerprint is not None:
        self._source_is_encrypted = True
        return str(data)
    logging.warning("Source was not encrypted!")
    return open(self.source, 'r', encoding='utf-8').read()


  def load(self):
    '''
    Override this to process a file with specific syntax
    :return:
    '''
    raise NotImplementedError()


  def recipients(self):
    '''
    Get the list of recipients from the file.

    :return: list
    '''
    return self._recipients


  def keys(self):
    '''
    Get the list of keys to entries in the file.

    :return: list of string
    '''
    return list(self.data.keys())


  def entry(self, key):
    '''
    Get a specific entry

    :param key: key to entry
    :return: Dictionary of entries
    '''
    try:
      return self.data[key]
    except KeyError as e:
      logging.error("Key '%s' not found.", key)
    return {}


  def password(self, key):
    '''
    Get the password at specified key

    :param key: string
    :return: string
    '''
    v = self.entry(key)
    return v['password']


  def encryptCommand(self):
    '''
    Show bash command to encrypt the source

    :return: string
    '''
    source_name = self.source
    if self._source_is_encrypted:
      source_name = os.path.splitext(self.source)[0]
    command = "gpg -e -s \ \n"
    for recipient in self.recipients():
      command += ' -r "{}" \ \n'.format(recipient)
    command += ' "' + source_name + '"'
    return command

