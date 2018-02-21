import configparser
import ast
import base64
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR,'data','config.ini'))


# aws_credentials
try:
	aws_access_key_id = config['aws_credentials']['aws_access_key_id']
	aws_secret_access_key = config['aws_credentials']['aws_secret_access_key']
	region = config['aws_credentials']['region']

except KeyError,e:
	error_info = "configure {} in config.ini. Refer config_sample.ini at {} for more info".format(e,BASE_DIR)
	sys.exit(error_info)

# instance_settings
try:
	image_id = 'ami-73f4a61c' ## do not change the ami-id
	security_group_ids = ast.literal_eval(config['instance_settings']['security_group_ids'])
	key_name = config['instance_settings']['key_name']
	volume_size = int(config['instance_settings']['volume_size'])
	instance_type = config['instance_settings']['instance_type']
	spot_price = config['instance_settings']['spot_price']
except KeyError,e:
	error_info = "configure {} in config.ini. Refer config_sample.ini at {} for more info".format(e,BASE_DIR)
	sys.exit(error_info)



file = open(os.path.join(BASE_DIR,"data","boot.sh"), "r")
user_data = file.read().strip()

file.close()