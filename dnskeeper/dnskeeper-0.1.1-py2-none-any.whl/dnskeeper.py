#!/usr/bin/env python

from tabulate import tabulate
import argparse
import cloudflare
import ConfigParser
import local
import inspect
import json
import os
import re
import sys

__version__ = "0.1.1"

CONFIGPATH = os.path.expanduser('~') + '/.cloudflare.cfg'
ZONES_DIR = ""

DRY_RUN=False

class DNSKeeper(object):
	def __init__(self):
		parser = argparse.ArgumentParser(
			description='Tool for managing Cloudflare DNS, by Liferay',
			usage='''dnskeeper <command> [<args>]

The available dnskeeper commands are:
	config		Create config file for dnskeeper
	diff		Display differences between local state and Cloudflare
	pull		Overwrite local records with current state
	push		Deploy changes to Cloudflare
	show		Show current state in Cloudflare
	validate	Test records file for proper formatting
''')

		parser.add_argument('command', help='Subcommand to run')
		# parse_args defaults to [1:] for args, but you need to
		# exclude the rest of the args too, or validation will fail

		args = parser.parse_args(sys.argv[1:2])

		if not hasattr(self, args.command):
			print 'Unrecognized command'

			parser.print_help()

			exit(1)

		if not args.command == "config":
			read_config()

		# use dispatch pattern to invoke method with same name
		getattr(self, args.command)()

	def config(self):
		parser = argparse.ArgumentParser(
			description='Create config files for dnskeeper')

		parser.add_argument('-e', '--email', help='email address for Cloudflare user')
		parser.add_argument('-k', '--api-key', help='api key for Cloudflare user')
		parser.add_argument('-z', '--zones-dir', help='path to store zone files')

		args = parser.parse_args(sys.argv[2:])

		create_config(args)

	def diff(self):
		parser = argparse.ArgumentParser(
			description='Display differences between local state and Cloudflare')

		parser.add_argument('domain')

		args = parser.parse_args(sys.argv[2:])

		print 'Running dnskeeper diff, domain=%s' % args.domain

		diff_records(args)

	def pull(self):
		parser = argparse.ArgumentParser(
			description='Overwrite local records with current state')

		parser.add_argument('domain')

		args = parser.parse_args(sys.argv[2:])

		pull_records(args)

	def push(self):
		parser = argparse.ArgumentParser(
			description='Deploy changes to Cloudflare')

		parser.add_argument('domain')
		parser.add_argument('-d', '--dry-run', action="store_false", help='simulates the actions that would occur')
		parser.add_argument('-o', '--output', choices=['json', 'simple', 'table'], default='table')

		args = parser.parse_args(sys.argv[2:])

		push_records(args)

	def show(self):
		parser = argparse.ArgumentParser(
			description='Show current state from Cloudflare')

		parser.add_argument('domain')
		parser.add_argument('-o', '--output', choices=['json', 'simple', 'table'], default='table')

		args = parser.parse_args(sys.argv[2:])

		show_records(args)

	def validate(self):
		parser = argparse.ArgumentParser(
			description='Test records file for proper formatting')

		parser.add_argument('domain')

		args = parser.parse_args(sys.argv[2:])

		validate_zone(args.domain)

def create_config(args):
	if args.email:
		email = args.email
	else:
		email = raw_input("Please enter email address for Cloudflare user: ")
	
	if args.api_key:
		api_key = args.api_key
	else:
		api_key = raw_input("Please enter your Cloudflare API key: ")
	
	if args.zones_dir:
		zones_dir = args.zones_dir
	else:
		zones_dir = raw_input("Please enter the path for your zones files [~/.dnskeeper/zones]: ") or os.path.expanduser('~') + '/.dnskeeper/zones/'

	cloudflare_config = '''[CloudFlare]
email = %s
token = %s

[dnskeeper]
zones_dir = %s
''' % (email, api_key, zones_dir)

	with open(CONFIGPATH, "w") as cloudflare_config_file:
		cloudflare_config_file.write(cloudflare_config)

def diff_records(args):
	
	#
	# WIP
	#

	return True

def format_output(data, output):
	if output == 'table' or output == 'simple':
		board = []

		for structure in data.items():
			if len(data[structure[0]]) > 0:
				if structure[0] == 'new_records':
					board_title = "New Records"
					headers = ['id', 'name', 'type', 'content', 'proxied', 'ttl']

					for record in data['new_records'].iteritems():
						board.append([record[0], record[1]['name'], record[1]['type'], record[1]['content'], record[1]['proxied'], record[1]['ttl']])

				elif structure[0] == 'deleted_records':
					board_title = 'Deleted Records'
					headers = ['id', 'name', 'type', 'content', 'proxied', 'ttl']

					for record in data['deleted_records'].iteritems():
						board.append([record[0], record[1]['name'], record[1]['type'], record[1]['content'], record[1]['proxied'], record[1]['ttl']])

				elif structure[0] == 'updated_records':
					board_title = "Updated Records"
					headers = ['id', 'status', 'name', 'type', 'content', 'proxied', 'ttl']

					for record in data['updated_records'].iteritems():
						board.append([
							record[0],
							'old',
							record[1]['old']['name'],
							record[1]['old']['type'],
							record[1]['old']['content'],
							record[1]['old']['proxied'],
							record[1]['old']['ttl']
							])
						board.append([
							record[0],
							'updated',
							record[1]['updated']['name'],
							record[1]['updated']['type'],
							record[1]['updated']['content'],
							record[1]['updated']['proxied'],
							record[1]['updated']['ttl']
							])

				if output == 'table':
					print tabulate(board, headers, tablefmt='fancy_grid')

				else:
					print tabulate(board, headers, tablefmt='simple')

	elif output == 'json':
		print json.dumps(data, indent=4, sort_keys=True)

def read_config():
	
	config = ConfigParser.RawConfigParser()
	config.read([CONFIGPATH])

	global ZONES_DIR
	ZONES_DIR = os.path.join(re.sub(r"\s+", '', config.get('dnskeeper', 'zones_dir')), '')
	
	if not os.path.exists(os.path.dirname(ZONES_DIR)):
		os.makedirs(os.path.dirname(ZONES_DIR))
	
def show_records(args):
	records = cloudflare.read_records(args.domain)

	output = args.output

	if output == 'table' or output == 'simple':
		board = []
		headers = ['id', 'name', 'type', 'content', 'proxied', 'ttl']

		for record in records.iteritems():
			board.append([record[0], record[1]['name'], record[1]['type'], record[1]['content'], record[1]['proxied'], record[1]['ttl']])

		if output == 'table':
			print tabulate(board, headers, tablefmt='fancy_grid')
		else:
			print tabulate(board, headers, tablefmt='simple')

	elif output == 'json':
		print json.dumps(records, indent=4, sort_keys=True)

def pull_records(args):
	records = cloudflare.read_records(args.domain)

	local.write_records(ZONES_DIR, args.domain, records)

	print 'Records written to ' + ZONES_DIR + args.domain + '.json'

def push_records(args):
	changes = {}

	if args.dry_run:
		global DRY_RUN
		DRY_RUN=True

	#
	# Ensure local records file is valid JSON structure.
	#

	validate_zone(args.domain_name)

	#
	# Delete records from Cloudflare that are not present locally.
	#

	changes['deleted_records'] = delete_unwanted_records(args.domain)

	#
	# Add records to Cloudflare that are only present locally.
	#
	# NOTE: This requires two steps, because we need to gran the updated_local_records['local_records'] dictionary to update our local
	# config with the record IDs from Cloudflare for the newly generated records.
	#

	updated_local_records = add_new_records(args.domain)

	changes['new_records'] = updated_local_records['new_records']

	if not DRY_RUN:
		local.write_records(ZONES_DIR, args.domain, updated_local_records['local_records'])

	#
	# Updates records in Cloudflare that have changed values locally.
	#

	changes['updated_records'] = sync_existing_records(args.domain)

	format_output(changes, args.output)

def sync_existing_records(domain_name):
	cloudflare_records = cloudflare.read_records(domain_name)
	local_records = local.read_records(ZONES_DIR, domain_name)
	records_state = {}

	for record_id in local_records:
		if local_records[record_id] != cloudflare_records[record_id]:
			cloudflare.update_record(domain_name, record_id, local_records[record_id], DRY_RUN)
			records_state[record_id] = {}
			records_state[record_id]['old'] = cloudflare_records[record_id]
			records_state[record_id]['updated'] = local_records[record_id]

	return records_state

def delete_unwanted_records(domain_name):
	cloudflare_records = cloudflare.read_records(domain_name)
	local_records = local.read_records(ZONES_DIR, domain_name)

	records_state = {}

	for cloudflare_record in cloudflare_records:
		if cloudflare_record not in local_records:
			record_data = cloudflare_records[cloudflare_record]

			records_state[cloudflare_record] = {
				'content': record_data['content'],
				'name': record_data['name'],
				'proxied': record_data['proxied'],
				'ttl': record_data['ttl'],
				'type': record_data['type']
			}

			cloudflare.delete_record(domain_name, cloudflare_record, DRY_RUN)

	return records_state

def add_new_records(domain_name):
	cloudflare_records = cloudflare.read_records(domain_name)
	local_records = local.read_records(ZONES_DIR, domain_name)

	local_records_loop = local_records.copy()

	records_state = {}
	records_state['local_records'] = {}
	records_state['new_records'] = {}

	for local_record in local_records_loop:
		if local_record not in cloudflare_records:
			# add record
			new_record = cloudflare.add_record(domain_name, local_records_loop[local_record], DRY_RUN)

			records_state['new_records'][new_record['id']] = {
				'content': new_record['content'],
				'name': new_record['name'],
				'proxied': new_record['proxied'],
				'ttl': new_record['ttl'],
				'type': new_record['type']
			}

			local_records[new_record['id']] = local_records.pop(local_record)

	records_state['local_records'] = local_records

	return records_state

def main():
	DNSKeeper()

def validate_zone(domain_name):
	valid = local.validate_records(ZONES_DIR, domain_name)

	if not valid:
		exit()