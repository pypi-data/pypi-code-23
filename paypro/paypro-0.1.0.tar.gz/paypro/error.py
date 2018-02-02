class PayProError(Exception):
  pass

class ApiConnectionError(PayProError):
  pass

class InvalidResponseError(PayProError):
  pass