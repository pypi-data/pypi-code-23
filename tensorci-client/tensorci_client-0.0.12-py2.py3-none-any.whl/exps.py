class TensorCIException(BaseException):

  def __init__(self, message=None):
    self.message = message


class MissingCredentialsException(TensorCIException):

  def __init__(self, missing_creds=None):
    self.missing_creds = missing_creds or []
    message = None

    if self.missing_creds:
      message = 'Missing TensorCI credentials:\n'
      missing_cred_temp = '{} -- either set {} during instantiation of TensorCI or set the {} environment variable.\n'

      for c in self.missing_creds:
        attr, backup = c
        message += missing_cred_temp.format(attr, attr, backup)

    super(MissingCredentialsException, self).__init__(message)


class SocketRequestException(TensorCIException):

  def __init__(self, message='Unknown Exception Occurred'):
    super(SocketRequestException, self).__init__(message)


class ResponseParseException(TensorCIException):

  def __init__(self, resp=None):
    message = 'Error parsing JSON response: {}'.format(resp)
    super(ResponseParseException, self).__init__(message)


class ResponseError(TensorCIException):

  def __init__(self, resp=None):
    status = resp.get('status')
    err = resp.get('error')
    message = 'Request returned error'

    if status:
      message += ' (status={})'.format(status)

    if err:
      message += ': {}'.format(err)

    super(ResponseError, self).__init__(message)