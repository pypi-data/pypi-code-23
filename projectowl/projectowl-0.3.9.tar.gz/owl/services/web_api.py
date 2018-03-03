"""Generic interface for web apis.
"""

import abc

from flask import Flask
from flask_cors import CORS

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


def make_success_res_obj(data, code=200):
  """Create a successful response object.

  Args:
    data: any object to attach to the result.
  """
  return {"status": {"code": code, "msg": "Ok"}, "data": data}


def make_error_res_obj(err_msg, code=500):
  """Create an error response object.

  Args:
    err_msg: error message string.
  """
  return {"error": {"code": code, "msg": err_msg}}


class WebAPIBase(object):
  """Template class for web api services.
  """
  __metaclass__ = abc.ABCMeta

  app = None
  started = False
  name = ""

  def __init__(self, api_name):
    self.name = api_name
    self.app = Flask(__name__)
    CORS(self.app, resources={r"/*": {"origins": "*"}})
    self.add_resource("/", ["GET"], self.index)
    self.add_resource("/info", ["GET"], self.info)

  def add_resource(self, path, method_list, func):
    """Add resources to api.

    Args:
      path: e.g. "/info/".
      method_list: e.g. ["GET", "POST"].
      func: function.
    """
    self.app.add_url_rule(path, methods=method_list, view_func=func)

  def index(self):
    return "Welcome to {} API.".format(self.name)

  def info(self):
    pass

  @abc.abstractmethod
  def prepare(self):
    """Prepare resources before starting the api.
    """
    pass

  def start(self, debug=False, port=5000):
    """Start running the api.
    """
    if not self.started:
      self.prepare()
    if debug:
      self.app.run(debug=True, port=port)
    else:
      http_server = HTTPServer(WSGIContainer(self.app))
      http_server.listen(port)
      print "service on"
      IOLoop.instance().start()