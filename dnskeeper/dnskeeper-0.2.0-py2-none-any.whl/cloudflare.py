#!/usr/bin/env python

import CloudFlare
import json

cf = CloudFlare.CloudFlare()

def add_record(domain_name, record, dry_run=False):
	zone_id = _get_zone_id_by_name(domain_name)

	if not dry_run:
		newRecord = cf.zones.dns_records.post(zone_id, data=record)
	else:
		newRecord = record
		record['id'] = _compute_random() + 'GENERATEDID' + _compute_random()
	
	return newRecord

def delete_record(domain_name, record_id, dry_run=False):
	zone_id = _get_zone_id_by_name(domain_name)

	if not dry_run:
		cf.zones.dns_records.delete(zone_id, record_id)

def read_records(domain_name):
	cf = CloudFlare.CloudFlare(raw=True)
	cloudflare_records = {}
	page_number = 0
	zone_id = _get_zone_id_by_name(domain_name)

	while True:
		page_number += 1
		raw_results = cf.zones.dns_records.get(zone_id, params={'page': page_number, 'per_page': 100})
		raw_records = raw_results['result']


		for dns_record in raw_records:
			cloudflare_records[dns_record['id'].encode('utf8')] = {
				'content': dns_record['content'].encode('utf8'),
				'name': dns_record['name'].encode('utf8'),
				'proxied': dns_record['proxied'],
				'ttl': dns_record['ttl'],
				'type': dns_record['type'].encode('utf8')
			}

		total_pages = raw_results['result_info']['total_pages']
		
		if page_number == total_pages:
			break

	return cloudflare_records

def update_record(domain_name, record_id, record_data, dry_run=False):
	zone_id = _get_zone_id_by_name(domain_name)
	
	if not dry_run:
		cf.zones.dns_records.put(zone_id, record_id, data=record_data)
	
def _compute_random():
	return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(6))

def _compute_random():
	return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(6))

def _get_zone_id_by_name(zone_name):
	"""Returns the Cloudflare Zone ID for the requested domain name

	Args:
		name (str): Domain name to return Zone ID for
	"""
	try:
		zones = cf.zones.get(params = {'name':zone_name,'per_page':1})
	except CloudFlare.exceptions.CloudFlareAPIError as e:
		exit('/zones.get %d %s - api call failed' % (e, e))
	except Exception as e:
		exit('/zones.get - %s - api call failed' % (e))

	if len(zones) == 0:
		exit('No zones found')

	# extract the zone_id which is needed to process that zone
	return zones[0]['id']