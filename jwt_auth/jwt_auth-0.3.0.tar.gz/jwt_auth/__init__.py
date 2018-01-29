from json import JSONEncoder
from uuid import UUID
from datetime import datetime
default_encoder = JSONEncoder.default

class UUIDEncoder(JSONEncoder):
  	def default(self, obj):
				if isinstance(obj, UUID):
					return 	str(obj)
				if isinstance(obj, datetime):
					return 	obj.isoformat()
				return default_encoder(self, obj)

JSONEncoder.default = UUIDEncoder.default
