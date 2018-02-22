# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import hashlib
import hmac
import time
import ssl
from .exceptions import SSLError


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
	return clientId + '|securemode=' + str(securemode) + ',signmethod=' + signmethod + ',timestamp=' + ts + '|'


def create_signature(secretKey, string, signmethod='hmacsha1'):
	string_to_sign = string.encode('utf-8')

	if signmethod == 'hmacsha1':
		hashed = hmac.new(secretKey, string_to_sign, hashlib.sha1)
	elif signmethod == 'hmacmd5':
		hashed = hmac.new(secretKey, string_to_sign, hashlib.md5)

	return hashed.hexdigest().upper()


def getAliyunIotMqttClient(productKey, deviceName, deviceSecret, clientId, securemode=2,
						   signmethod='hmacsha1', tslCertPath='root.cer'):
	mqttClientId = get_client_id(clientId, securemode, signmethod)
	client = AliyunIotMqttClient(mqttClientId)
	userName = deviceName + '&' + productKey
	ordered_keys = get_sort_keys(productKey, deviceName, clientId)
	password = create_signature(deviceSecret, ordered_keys)

	if securemode == 2:
		if tslCertPath is None:
			raise SSLError('empyt ssl perm path')
		client.tls_set(ca_certs=tslCertPath, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED,
					   tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
		client.tls_insecure_set(False)

	client.username_pw_set(userName, password=password)

	return client


class AliyunIotMqttClient(mqtt.Client):
	def __init__(self, *args, **kwargs):
		super(AliyunIotMqttClient, self).__init__(*args, **kwargs)
