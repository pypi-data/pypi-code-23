#!/usr/bin/env python

import json

def read_records(zones_dir, domain_name):
    localZoneConfig = zones_dir + domain_name + '.json'

    with open(localZoneConfig) as json_data:
		localRecords = json.load(json_data)
    
    return localRecords

def write_records(zones_dir, domain_name, records):
    localZoneConfig = zones_dir + domain_name + '.json'

    with open(localZoneConfig, "w") as json_data:
		json_data.write(json.dumps(records, indent=4, sort_keys=True))

def validate_records(zones_dir, domain_name):
  localZoneConfig = zones_dir + domain_name + '.json'
  
  try:
    with open(localZoneConfig) as json_data:
      json.load(json_data)
    
    print "Records file is valid json."
    
    return True
  except ValueError as error:
    print localZoneConfig + ": invalid json in file: %s" % error
    
    return False