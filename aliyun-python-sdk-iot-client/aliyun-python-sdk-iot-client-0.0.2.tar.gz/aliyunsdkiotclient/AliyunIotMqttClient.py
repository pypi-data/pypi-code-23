# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
from hashlib import sha1
import hmac
import time
import ssl
from .exceptions import (
	Timeout,
	HTTPError, ConnectionError,
	FileModeWarning, ConnectTimeout, ReadTimeout, SSLError
)


def get_sort_keys(productKey, deviceName, clientId):
	ts = str(int(time.time()))
	d = {'productKey': productKey, 'deviceName': deviceName, 'timestamp': ts, 'clientId': clientId}
	sort_d = [(k, d[k]) for k in sorted(d.keys())]

	content = ''
	for i in sort_d:
		content += str(i[0])
		content += str(i[1])

	return content


def get_client_id(clientId, securemode=2, signmethod='hmacsha1'):
	ts = str(int(time.time()))
	return clientId + '|securemode=' + str(securemode) + ',signmethod=' + signmethod + 'timestamp=' + ts + '|'


def create_signature(secret_key, string):
	string_to_sign = string.encode('utf-8')
	hashed = hmac.new(secret_key, string_to_sign, sha1)
	return hashed.hexdigest().upper()


class AliyunIotMqttClient(mqtt):
	def __init__(self, clientId):
		self.clientId = clientId
		super(AliyunIotMqttClient, self).__init__(clientId)

	def getAliyunIotMqttClient(self, productKey, deviceName, deviceSecret, securemode=2,
							   signmethod='hmacsha1', tslCertPath='data/root.cer'):
		mqttClientId = get_client_id(self.clientId, securemode, signmethod)

		client = AliyunIotMqttClient(mqttClientId)
		userName = deviceName + '&' + productKey
		ordered_keys = get_sort_keys(productKey, deviceName, self.clientId)
		password = create_signature(deviceSecret, ordered_keys)

		if securemode == 2:
			if tslCertPath is None:
				raise SSLError('empyt ssl perm path')
			client.tls_set(ca_certs=tslCertPath, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED,
						   tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
			client.tls_insecure_set(False)

		client.username_pw_set(userName, password=password)

		return client



