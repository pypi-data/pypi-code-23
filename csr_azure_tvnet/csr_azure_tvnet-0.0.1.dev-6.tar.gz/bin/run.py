#!/usr/bin/env python

'''
Cisco Copyright 2017

Author: Vamsi Kalapala

RUN.PY


'''

import os
import time
import parse
import argparse
from configs import *
from datetime import datetime
from azurestorage import azsto
from dmvpn import configure_transit_vnet,get_interfaces_ips
import logging


def setup_logging():
	log = logging.getLogger('dmvpn')

	DIR = '/home/guestshell'
	logfile_name = 'tvnetlog_' + str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')) + '.txt'
	print(logfile_name, DIR)
	hdlr = logging.FileHandler(os.path.join(DIR,logfile_name))
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	log.addHandler(hdlr) 
	log.setLevel(logging.INFO)

def main(args):
	'''
	MAIN function starts all the necessary stuff

	TBD

	'''
	
	section_dict = parse.parse_decoded_custom_data(args.decoded)
	storage_object = azsto(section_dict['strgacctname'], section_dict['strgacckey'])
	section_dict = parse.setup_file_dict(section_dict)
	section_dict['storage_object']  = storage_object

	if 'spoke' in section_dict['role']:		
		section_dict = parse.get_all_files(section_dict)
	elif 'hub-2' in section_dict['role']:
		section_dict = parse.get_all_files(section_dict, ['dmvpn'])
	
	section_dict = parse.setup_default_dict(section_dict)

	configure_transit_vnet(section_dict)



if __name__ == '__main__': # pragma: no cover
	setup_logging()
	parser = argparse.ArgumentParser()
	parser.add_argument('-d','--decoded', type=str, default="sampledecodedCustomData", help='File location for the decoded custom data')
	args = parser.parse_args()
	main(args)