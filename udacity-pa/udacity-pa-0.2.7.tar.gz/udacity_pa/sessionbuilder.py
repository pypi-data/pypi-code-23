from __future__ import absolute_import, division, print_function, unicode_literals
from future import standard_library
from future.utils import bytes_to_native_str
standard_library.install_aliases()
from builtins import input
from builtins import object

import os
import sys
import json
import re
import getpass
import errno
import copy
import requests
from urllib.parse import urlsplit

HOTH_URL = "https://hoth.udacity.com"

class ProjectAssistantAuthenticationError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return self.value

def default_app_data_dir():
  APPNAME = "udacity-pa"
  if sys.platform == 'win32':
    return os.path.join(os.environ['APPDATA'], APPNAME)
  else:
    return os.path.expanduser(os.path.join("~", "." + APPNAME))

def default_jwt_paths():
  return [os.path.join(os.getcwd(), 'jwt'), os.path.join(default_app_data_dir(), 'jwt')]

class SessionBuilder():
  def __init__(self, root_url, jwt_path):
    self.root_url = root_url
    self.jwt_path = jwt_path

    if self.jwt_path is None:
      for p in default_jwt_paths():
        if os.path.isfile(p):
          self.jwt_path = p
          break

  def new(self):
    session = requests.Session()
    session.headers.update({'content-type':'application/json', 'accept': 'application/json'})

    jwt = self.load_jwt_from_file()

    if jwt is None or not self.jwt_works(jwt):
      jwt = self.login_for_jwt()

      if jwt is None or not self.jwt_works(jwt):
        raise ProjectAssistantAuthenticationError("Authentication Failed.")

      save = input("Save login token to %s?[y,N]" % self.jwt_path)
      if save.lower() == 'y':
        self.save_the_jwt(jwt)

    self.set_auth_headers(session, jwt)

    return session

  def set_auth_headers(self, session, jwt):
    session.headers.update({'authorization': 'Bearer ' + jwt})

  def jwt_works(self, jwt):
    session = requests.Session()
    session.headers.update({'content-type':'application/json', 'accept': 'application/json'})

    self.set_auth_headers(session, jwt)

    r = session.get(url = self.root_url + '/users/me')

    return r.status_code == 200

  def save_the_jwt(self, jwt):
    try:
      os.makedirs(os.path.dirname(self.jwt_path))
    except OSError as exception:
      if exception.errno != errno.EEXIST:
        raise

    with open(self.jwt_path, "w") as fd:
      fd.write(jwt)


  def load_jwt_from_file(self):
    try:
      with open(self.jwt_path, "r") as fd:
        jwt = fd.read().rstrip()

      if not jwt or not self.jwt_works(jwt):
        jwt = None
    except (requests.exceptions.HTTPError, IOError, ValueError, KeyError) as e:
      jwt = None

    return jwt

  def login_for_jwt(self):
    try:
      session = requests.Session()
      session.headers.update({'content-type':'application/json', 'accept': 'application/json'})

      password_prompt = bytes_to_native_str(b"Password :")

      print("Udacity Login required.")
      email = input('Email :')
      password = getpass.getpass(password_prompt)
      udacity_login(session, self.root_url, email, password)
    except requests.exceptions.HTTPError as e:
      if e.response.status_code == 403:
        raise ProjectAssistantAuthenticationError("Authentication failed")
      else:
        raise e

    try:
      r = session.post(self.root_url + '/auth_tokens')
      r.raise_for_status()
    except:
      raise ProjectAssistantAuthenticationError("Authentication failed")

    jwt = r.json()['auth_token']

    return jwt

#Helper functions for logins
def udacity_login(http, root_url, email, password):
  data = {'email' : email, 'password' : password, "next": root_url + "/auth/udacity/callback"}

  #Logging into udacity
  r = http.post(HOTH_URL + '/v2/authenticate', 
                data=data,
                headers={"content-type": "application/x-www-form-urlencoded", "accept": "*/*"})
  r.raise_for_status()
