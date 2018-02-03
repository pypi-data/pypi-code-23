import os

from consulate import Session

from .decorator import with_retry_connections
from .exception import CoreException
from six import iteritems
import json


class Consulate(object):
	def __init__(self, app=None, **kwargs):
		self.kwargs = kwargs
		self.app = app
		self.host = self.kwargs.get('consul_host') or os.environ.get('CONSUL_HOST', 'localhost')
		self.port = self.kwargs.get('consul_port') or os.environ.get('CONSUL_PORT', 8500)
		self.max_tries = self.kwargs.get('max_tries', 3)
		self.session = None
		if app is not None:
			self.init_app(app)
		
	def init_app(self, app):
		self.app = app
		if not hasattr(app, 'extensions'):
			app.extensions = {}
		if 'consul' in app.extensions:
			raise CoreException('Flask application already initialized')
		self.session = self.create_session(test_connection=self.kwargs.get('test_connection', False))
		
	@with_retry_connections()
	def create_session(self, test_connection=False):
		session = Session(host=self.host, port=self.port)
		if test_connection:
			session.status.leader()
		return session
	
	@with_retry_connections()
	def register(self, **kwargs):
		kwargs.setdefault('name', self.app.name)
		self.session.agent.service.register(**kwargs)
		
	def load_config(self, namespace=None):
		if namespace is None:
			namespace = "config/{service}/{environment}/".format(
				service=os.environ.get('SERVICE', 'generic_service'),
				environment=os.environ.get('ENVIRONMENT', 'generic_environment')
			)
		
		for k, v in self.session.kv.find(namespace).items():
			k = k.replace(namespace, '')
			try:
				data = json.loads(v)
				for key, value in data.items():
					self.app.config[key] = value
				
			except (TypeError, ValueError):
				self.app.logger.info("Couldn't de-serialize {} to json, using raw value".format(v))
				self.app.config[k] = v