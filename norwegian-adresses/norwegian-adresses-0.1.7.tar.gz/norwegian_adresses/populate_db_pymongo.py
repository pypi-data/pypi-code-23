"""Populate database with adresses"""
import json
import sys
from time import time

if __name__ == '__main__':
    from model_pymongo import collection
else:
    from .model_pymongo import collection


def populate_db(data, fields, **kwargs):
    """Poulate a db with adresses."""
    time1 = time()
    output_interval = .1
    last_output = output_interval
    addreses = []
    for idx, entry in enumerate(data):
        # Insert an Address in the address table
        try:
            new_address = {}
            if not fields:
                raise KeyError('Missing fields-argument.')
            else:
                for key, val in fields.items():
                    value = val[0](entry.get(val[1]))
                    if value:
                        new_address[key] = value

            addreses.append(new_address)
        except ValueError:
            pass
        if (time() - time1) >= last_output:
            last_output += output_interval
            print('{:0.1f}% done.'.format(
                (idx) / len(data) * 100
            ))
    print('Saving all entries to database')
    collection.insert_many(addreses)
    print('Done')


def json_to_db(json_file, fields, **kwargs):
    """Retrieve all entries in a json-file and add it to db.."""
    with open(json_file) as data_file:
        address_data = json.load(data_file)
    populate_db(address_data, fields, **kwargs)


if __name__ == "__main__":
    from pprint import pprint
    pprint(collection.count())
    if "--setup" in sys.argv:
        print('Dropping and reacreating database')
        collection.drop()
        json_to_db(
            'data/adresser.json',
            fields={
                'street_name_lc': [str, 'vei'],
                'street_name': [str, 'vei_formatted'],
                'post_code': [int, 'postnummer'],
                'post_area': [str, 'postnummeromrade'],
                'place_lc': [str, 'tettsted'],
                'place': [str, 'tettsted_formatted'],
                'loc': [list, 'loc'],
            },
        )
