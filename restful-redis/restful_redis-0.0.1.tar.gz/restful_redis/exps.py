class JsonParseException(BaseException):
  def __init__(self, request):
    self.message = 'Error parsing JSON: {}'.format(request)


class InvalidRequestException(BaseException):
  def __init__(self, body):
    self.message = 'Invalid request body received: {}. \'request_uid\' key required.'.format(body)


class RequestTimeout(BaseException):
  def __init__(self):
    self.message = 'Request timed out.'