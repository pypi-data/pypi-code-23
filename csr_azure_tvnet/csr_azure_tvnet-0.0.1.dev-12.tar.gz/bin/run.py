#!/usr/bin/env python

'''
Cisco Copyright 2018
Author: Vamsi Kalapala <vakalapa@cisco.com>

FILENAME: RUN.PY


'''

import os
import time
import parse
import argparse
from configs import *
from shutil import copyfile
from datetime import datetime
from azurestorage import azsto
from dmvpn import configure_transit_vnet,get_interfaces_ips
import logging


def setup_directory(tvnet_home='/home/guestshell/azure_tvnet'):
	'''
	This function will help with setting up directory structure.

	'''
	folder_list = ['logs', 'data','bin']
	if not os.path.exists(tvnet_home):
		os.makedirs(tvnet_home)
	for folder in folder_list:
		folder_path = os.path.join(tvnet_home, folder)
		if not os.path.exists(folder_path):
			os.makedirs(folder_path)
	return tvnet_home

def copy_custom_data_file(file, tvnet_home):
	dest = os.path.join(tvnet_home, 'customdata.txt')
	if not os.path.exists(dest):
		if os.path.exists(file):
			copyfile(file,dest)
		else:
			log.error('FATAL ERROR: No custom data file found!')
			return False
	return dest

def setup_logging(tvnet_home):
	log = logging.getLogger('dmvpn')
	folder = 'logs'
	logfile_name = 'tvnetlog_' + str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')) + '.txt'
	hdlr = logging.FileHandler(os.path.join(tvnet_home,'log',logfile_name))
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	log.addHandler(hdlr) 
	log.setLevel(logging.INFO)

def main(args):
	'''
	MAIN function starts all the necessary stuff

	TBD

	'''

	new_cd_file = copy_custom_data_file(args.decoded, tvnet_home)
	if not new_cd_file:
		return False

	section_dict = parse.parse_decoded_custom_data(new_cd_file)
	if not section_dict:
		log.error('FATAL ERROR: There are no details found in customdata file')
		print('FATAL ERROR: There are no details found in customdata file')
		return False
	
	try:
		storage_object = azsto(section_dict['strgacctname'], section_dict['strgacckey'])
		section_dict['storage_object']  = storage_object
	except KeyError:
		log.error('FATAL ERROR: strgacctname or strgacckey are not found!')
		print('FATAL ERROR: strgacctname or strgacckey are not found!')
		return False

	section_dict = parse.setup_file_dict(section_dict)

	if 'spoke' in section_dict['role']:		
		section_dict = parse.get_all_files(section_dict)
	elif 'hub' in section_dict['role']:
		section_dict = parse.get_all_files(section_dict, ['dmvpn'])
	
	section_dict = parse.setup_default_dict(section_dict)

	configure_transit_vnet(section_dict)



if __name__ == '__main__': # pragma: no cover
	tvnet_home = setup_directory()
	setup_logging(tvnet_home)
	parser = argparse.ArgumentParser()
	parser.add_argument('-d','--decoded', type=str, default="sampledecodedCustomData", help='File location for the decoded custom data')
	args = parser.parse_args()
	main(args)