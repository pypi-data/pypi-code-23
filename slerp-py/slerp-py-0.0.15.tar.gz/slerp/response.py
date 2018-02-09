from flask import Response, jsonify
from .logger import logging

log = logging.getLogger(__name__)


class JsonResponse(Response):
	default_mimetype = 'application/json'
	
	@classmethod
	def force_type(cls, rv, environ=None):
		if isinstance(rv, dict):
			data = {}
			if 'status' not in rv:
				data.update({'status': 'OK'})
			else:
				data.update({'status': rv['status']})
			if 'message' in rv:
				data.update({'message': rv['message']})
			if 'key' in rv:
				data.update({'key': rv['key']})
			if 'total' in rv:
				data.update({'total': rv['total']})
				rv.pop('total')
			if 'total_pages' in rv:
				data.update({'total_pages': rv['total_pages']})
				rv.pop('total_pages')
			if 'payload' in rv:
				data.update({'payload': rv['payload']})
			
			return super(JsonResponse, cls).force_type(jsonify(data), environ)
		return super(JsonResponse, cls).force_type(rv, environ)