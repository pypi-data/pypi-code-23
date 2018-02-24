
class JSONParseException(BaseException):

  def __init__(self, request):
    self.message = 'Error parsing JSON: {}'.format(request)


class InvalidRequestException(BaseException):

  def __init__(self, body):
    self.message = 'Invalid request body received: {}. \'request_uid\' and \'target\' keys required.'.format(body)


class RequestTimeout(BaseException):

  def __init__(self):
    self.message = 'Request timed out.'


class ResponseError(BaseException):

  def __init__(self, message):
    self.message = message


class UnknownHandlerException(BaseException):

  def __init__(self, handler):
    self.message = 'Unknown handler specified: {}'.format(handler)