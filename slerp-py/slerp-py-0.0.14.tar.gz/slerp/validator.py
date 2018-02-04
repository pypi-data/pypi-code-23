import re
from slerp import is_empty, is_not_digit, is_blank
from .exception import ValidationException,CoreException


class Key(object):
	def __init__(self, keys):
		if not isinstance(keys, list):
			raise TypeError('keys.should.be.instance.of.list')
		self.keys = keys
	
	def __call__(self, original_function):
		def new_function(other, domain):
			if not isinstance(domain, dict):
				raise ValidationException('input.must.domain')
			for key in self.keys:
				if '.' in key:
					split = key.split('.')
					if split[0] not in domain:
						raise ValidationException('required.key', key=split[0])
					if isinstance(domain[split[0]], list):
						for k in split[1:]:
							for i, d in enumerate(domain[split[0]]):
								if k not in d:
									raise ValidationException('required.key', key='{}[{}]'.format(k, i))
					elif isinstance(domain[split[0]], dict):
						for k in split[1:]:
							if k not in domain[split[0]]:
								raise ValidationException('required.key', key='{}'.format(k))
					else:
						raise CoreException('object.type.unknown')
				else:
					if key not in domain:
						raise ValidationException('required.key', key=key)
			return original_function(other, domain)
		
		return new_function


class Empty(object):
	def __init__(self, keys):
		if not isinstance(keys, list):
			raise TypeError('keys.should.be.instance.of.list')
		self.keys = keys
		pass
	
	def __call__(self, original_function):
		@Key(self.keys)
		def new_function(other, domain):
			for key in self.keys:
				if '.' in key:
					split = key.split('.')
					if isinstance(domain[split[0]], list):
						for k in split[1:]:
							for i, d in enumerate(domain[split[0]]):
								if is_empty(d[k]):
									raise ValidationException('value.cannot.be.empty', key='{}[{}]'.format(k, i))
					elif isinstance(domain[split[0]], dict):
						for k in split[1:]:
							d = domain[split[0]]
							for k1 in d:
								if is_empty(d[k1]):
									raise ValidationException('value.cannot.be.empty', key='{}'.format(k))
					else:
						raise CoreException('object.type.unknown')
				else:
					if is_empty(domain[key]):
						raise ValidationException('value.cannot.be.empty', key=key)
			return original_function(other, domain)
		
		return new_function


class Blank(object):
	def __init__(self, keys):
		if not isinstance(keys, list):
			raise TypeError('keys.should.be.instance.of.list')
		self.keys = keys
		pass
	
	def __call__(self, original_function):
		@Key(self.keys)
		def new_function(other, domain):
			for key in self.keys:
				if '.' in key:
					split = key.split('.')
					if isinstance(domain[split[0]], list):
						for k in split[1:]:
							for i, d in enumerate(domain[split[0]]):
								if is_blank(d[k]):
									raise ValidationException('value.cannot.be.blank', key='{}[{}]'.format(k, i))
					elif isinstance(domain[split[0]], dict):
						for k in split[1:]:
							d = domain[split[0]]
							for k1 in d:
								if is_blank(d[k1]):
									raise ValidationException('value.cannot.be.blank', key='{}'.format(k))
					else:
						raise CoreException('object.type.unknown')
				else:
					if is_blank(domain[key]):
						raise ValidationException('value.cannot.be.blank', key=key)
			return original_function(other, domain)
		
		return new_function


class Number(object):
	def __init__(self, keys):
		if not isinstance(keys, list):
			raise ValidationException('keys.should.be.instance.of.list')
		self.keys = keys
		pass
	
	def __call__(self, original_function):
		@Key(self.keys)
		def new_function(other, domain):
			
			for key in self.keys:
				if '.' in key:
					split = key.split('.')
				
					if isinstance(domain[split[0]], list):
						for k in split[1:]:
							for i, d in enumerate(domain[split[0]]):
								if is_not_digit(d[k]):
									raise ValidationException('required.number.{}'.format(k), key='{}[{}]'.format(k, i))
					elif isinstance(domain[split[0]], dict):
						for k in split[1:]:
							d = domain[split[0]]
							for k1 in d:
								if is_not_digit(d[k1]):
									raise ValidationException('required.number.{}'.format(k), key='{}'.format(k))
					else:
						raise CoreException('object.type.unknown')
				else:
					if is_not_digit(str(domain[key])):
						raise ValidationException('required.number.' + key, key=key)
			return original_function(other, domain)
		
		return new_function


class Email(object):
	
	def __init__(self, keys):
		if not isinstance(keys, list):
			raise ValidationException('keys.should.be.instance.of.list')
		self.keys = keys
		self.mail_re = r"^[_A-Za-z0-9-\+]+(\.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]+(\.[A-Za-z0-9]+)*(\.[A-Za-z]{2,})$"
		pass
	
	def __call__(self, original_function):
		@Key(self.keys)
		def new_function(other, domain):
			for key in self.keys:
				if '.' in key:
					split = key.split('.')
					if isinstance(domain[split[0]], list):
						for k in split[1:]:
							for i, d in enumerate(domain[split[0]]):
								if not bool(re.match(self.mail_re, d[k])):
									raise ValidationException('invalid.email', key='{}[{}]'.format(k, i))
					elif isinstance(domain[split[0]], dict):
						for k in split[1:]:
							d = domain[split[0]]
							for k1 in d:
								if not bool(re.match(self.mail_re, d[k1])):
									raise ValidationException('invalid.email', key='{}'.format(k))
					else:
						raise CoreException('object.type.unknown')
				else:
					if not bool(re.match(self.mail_re, domain[key])):
						raise ValidationException('invalid.email', key=key)
			return original_function(other, domain)
		return new_function


class Phone(object):
	def __init__(self, keys):
		if not isinstance(keys, list):
			raise ValidationException('keys.should.be.instance.of.list')
		self.keys = keys
		self.phone_re = r"(\+[0-9]+[\- \.]*)?(\([0-9]+\)[\- \.]*)?([0-9][0-9\-\.]+[0-9])"
		pass
	
	def __call__(self, original_function):
		@Key(self.keys)
		def new_function(other, domain):
			if not isinstance(domain, dict):
				raise ValidationException('input.must.domain')
			for key in self.keys:
				if '.' in key:
					split = key.split('.')
					if isinstance(domain[split[0]], list):
						for k in split[1:]:
							for i, d in enumerate(domain[split[0]]):
								if not bool(re.match(self.phone_re, d[k])):
									raise ValidationException('invalid.phone.number.{}'.format(k), key='{}[{}]'.format(k, i))
					elif isinstance(domain[split[0]], dict):
						for k in split[1:]:
							d = domain[split[0]]
							for k1 in d:
								if not bool(re.match(self.phone_re, d[k1])):
									raise ValidationException('invalid.phone.number', key='{}'.format(k))
					else:
						raise CoreException('object.type.unknown')
				else:
					if not bool(re.match(self.phone_re, domain[key])):
						raise ValidationException('invalid.phone.number', key=key)
			return original_function(other, domain)
		return new_function


