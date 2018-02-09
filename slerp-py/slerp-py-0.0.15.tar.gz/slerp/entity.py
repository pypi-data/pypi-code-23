import json
from sqlalchemy.orm import class_mapper
from sqlalchemy.exc import DatabaseError
from .exception import CoreException
from .app import db


class Entity(object):
	__json_public__ = None
	__json_hidden__ = None
	__json_modifiers__ = None
	
	def __init__(self, obj):
		"""
		:rtype: object
		"""
		self.__mapper__ = None
		self.from_dict(self, obj)
		pass
	
	@staticmethod
	def from_dict(self, obj):
		for k, v in obj.items():
			if isinstance(v, dict):
				setattr(self, k, Entity(v))
			else:
				setattr(self, k, v)
	
	def save(self):
		db.session.add(self)
		self.flush()
	
	def delete(self):
		db.session.delete(self)
		self.flush()
	
	def update(self, obj):
		if obj is None:
			raise CoreException('object cannot be none')
		if not isinstance(obj, dict):
			raise CoreException('object must be instances of dict')
		for attr, value in obj.items():
			print ('{}:{}'.format(attr, value))
			setattr(self, attr, value)
		return self.save()
	
	@staticmethod
	def flush():
		try:
			db.session.flush()
		except DatabaseError:
			db.session.rollback()
			raise
	
	def get_field_names(self):
		for p in class_mapper(self.__class__).iterate_properties:
			yield p.key
	
	def to_dict(self):
		field_names = self.get_field_names()
		public = self.__json_public__ or field_names
		hidden = self.__json_hidden__ or []
		modifiers = self.__json_modifiers__ or dict()
		rv = dict()
		for key in public:
			value = getattr(self, key)
			if isinstance(value, list):
				child_list = []
				for v in value:
					child = {}
					for k in class_mapper(v.__class__).iterate_properties:
						child[k.key] = getattr(v, k.key)
					child_list.append(child)
				if len(child_list) > 0:
					rv.update({key: child_list})
				continue
			
			if issubclass(type(value), db.Model):
				child = {}
				for k in class_mapper(value.__class__).iterate_properties:
					child[k.key] = getattr(value, k.key)
					pass
				rv.update({key: child})
				continue
			
			if value is not None:
				rv[key] = value
		for key, modifier in modifiers.items():
			value = getattr(self, key)
			rv[key] = modifier(value, self)
		for key in hidden:
			rv.pop(key, None)
		return rv
	
	def to_json(self):
		return json.dump(self.to_dict())
