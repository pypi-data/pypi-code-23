from uuid import uuid4


def fresh_request_uid():
  return uuid4().hex