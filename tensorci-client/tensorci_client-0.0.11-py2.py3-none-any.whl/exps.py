class MissingCredentialsException(BaseException):

  def __init__(self, missing_creds=None):
    self.missing_creds = missing_creds or []
    self.message = None

    if self.missing_creds:
      self.message = 'Missing TensorCI credentials:\n'
      missing_cred_temp = '{} -- either set {} during instantiation of TensorCI or set the {} environment variable.\n'

      for c in self.missing_creds:
        attr, backup = c
        self.message += missing_cred_temp.format(attr, attr, backup)


class SocketRequestException(BaseException):

  def __init__(self, message='Unknown Exception Occurred'):
    self.message = message


class ResponseParseException(BaseException):

  def __init__(self, resp=None):
    self.message = 'Error parsing JSON response: {}'.format(resp)