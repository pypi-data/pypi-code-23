from json import JSONEncoder
from uuid import UUID
from datetime import datetime
default_encoder = JSONEncoder.default
from django.apps import AppConfig

class UUIDEncoder(JSONEncoder):
  	def default(self, obj):
				if isinstance(obj, UUID):
					return 	str(obj)
				if isinstance(obj, datetime):
					return 	obj.isoformat()
				return default_encoder(self, obj)

JSONEncoder.default = UUIDEncoder.default


class JWTAuthConfig(AppConfig):
	name = 'jwt_auth' 
	verbose_name = "用户中心"


default_app_config ='jwt_auth.JWTAuthConfig'