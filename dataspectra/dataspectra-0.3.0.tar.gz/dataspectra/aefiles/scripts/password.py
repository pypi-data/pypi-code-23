#!/usr/bin/env python2.7  

import base64

def passwordStatus(passwordStatus, username, password):
  def basicAuth(func):
    def callf(webappRequest, *args, **kwargs):
      # Parse the header to extract a user/password combo.
      # We're expecting something like "Basic XZxgZRTpbjpvcGVuIHYlc4FkZQ=="
      auth_header = webappRequest.request.headers.get('Authorization')

      if passwordStatus=="off":
        return func(webappRequest, *args, **kwargs)

      if auth_header == None:
        webappRequest.response.set_status(401, message="Authorization Required")
        webappRequest.response.headers['WWW-Authenticate'] = 'Basic realm="Unsecure Area"'
      else:
        # Isolate the encoded user/passwd and decode it
        auth_parts = auth_header.split(' ')
        user_pass_parts = base64.b64decode(auth_parts[1]).split(':')
        user_arg = user_pass_parts[0]
        pass_arg = user_pass_parts[1]

        if user_arg != username or pass_arg != password:
          webappRequest.response.set_status(401, message="Authorization Required")
          webappRequest.response.headers['WWW-Authenticate'] = 'Basic realm="Secure Area"'
        else:
          return func(webappRequest, *args, **kwargs)
    return callf
  return basicAuth
