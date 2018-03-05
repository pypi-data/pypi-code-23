import os

global home
home = os.environ["HOME"]

def get_path(req_type, key_type):
	return "%s/.csenet/%s/%s-key" % (home, req_type, key_type)

def has_key(req_type, key_type):
	return os.path.exists(get_path(req_type, key_type))

def get_key(req_type, key_type):
	with open(get_path(req_type, key_type)) as f:
		return f.read().rstrip().replace("\u0000", "")

def store_key(req_type, key_type, key):
	try: os.makedirs(home + "/.csenet/" + req_type)
	except: pass
	with open(get_path(req_type, key_type), 'w') as f:
			f.write(key)

def store_cert(name, cert):
	try: os.makedirs(home + "/.csenet/certs")
	except: pass
	with open(home + "/.csenet/certs/" + name + ".pem", 'w') as f:
		f.write(cert)

def store_private_key(name, key):
	try: os.makedirs(home + "/.csenet/private")
	except: pass
	with open(home + "/.csenet/private/" + name + ".key", 'w') as f:
		f.write(key)

def store_cacert(cert):
	try: os.makedirs(home + "/.csenet/ca")
	except: pass
	with open(home + "/.csenet/ca/cacert.pem", 'w') as f:
		f.write(cert)

