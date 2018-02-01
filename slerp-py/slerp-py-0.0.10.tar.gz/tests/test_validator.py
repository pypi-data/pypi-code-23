# from unittest import TestCase
#
#
# class TestValidator(TestCase):
# 	service = None
#
# 	def setUp(self):
# 		self.service = Service()
#
# 	def test_keys_fail(self):
# 		try:
# 			self.service.key_service({'user': {'name':'hell', 'alamat':'Jakarta'}})
# 		except ValidationException as e:
# 			self.assertEqual(e.key, 'nama')
# 			self.assertEqual(e.message, 'required.key')
#
# 	def test_keys_success(self):
# 		domain = self.service.key_service({'user': [{'nama': 'hell', 'alamat':''}, {'nama': 'hell', 'alamat':''}]})
# 		self.assertTrue('user' in domain)
# 		for data in domain['user']:
# 			self.assertTrue('nama' in data)
#
# 	def test_empty(self):
# 		try:
# 			self.service.value_service({'user': {'nama': ''}})
# 		except ValidationException as e:
# 			self.assertEqual(e.message, 'value.cannot.be.empty')
#
# 	def test_empty_success(self):
# 		domain = self.service.value_service({'user': {'nama': 'Rifky'}})
# 		self.assertTrue('user' in domain)
# 		self.assertTrue('nama' in domain['user'])
#
# 	def test_number_fail(self):
# 		try:
# 			self.service.number_service({'trx': {'trx_id': 'data'}})
# 		except ValidationException as e:
# 			self.assertEqual(e.message, 'required.number.trx_id')
# 			self.assertEqual(e.key, 'trx_id')
#
# 	def test_mail_fail(self):
# 		try:
# 			self.service.mail_service({'user': {'email': 'data'}})
# 		except ValidationException as e:
# 			self.assertEqual(e.message, 'invalid.email')
# 			self.assertEqual(e.key, 'email')
#
# 	def test_phone_fail(self):
# 		try:
# 			self.service.phone_service({'user': {'name': 'kiditz', 'phone': 'sa'}, 'alamat':'as'})
# 		except ValidationException as e:
# 			self.assertEqual(e.message, 'invalid.phone.number')
#
#
# class Service(object):
#
# 	@Key(['user.nama.alamat'])
# 	def key_service(self, domain):
# 		return domain
#
# 	@Email(['user.email'])
# 	def mail_service(self, domain):
# 		return domain
#
# 	@Empty(['user.nama'])
# 	def value_service(self, domain):
# 		return domain
#
# 	@Number(['trx.trx_id'])
# 	def number_service(self, domain):
# 		return domain
#
# 	@Blank(['user.name.phone', 'alamat'])
# 	@Phone(['user.phone'])
# 	def phone_service(self, domain):
# 		return domain