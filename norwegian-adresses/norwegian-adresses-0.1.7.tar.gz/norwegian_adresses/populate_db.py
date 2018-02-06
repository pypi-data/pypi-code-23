"""Populate database with adresses"""
import json
import sys
from time import time

if __name__ == '__main__':
    from model import Address, Base, session, engine
else:
    from .model import Address, Base, session, engine


def populate_db(data, **kwargs):
    """Poulate a db with adresses."""
    time1 = time()
    output_interval = .5
    last_output = output_interval
    for idx, entry in enumerate(data):
        # Insert an Address in the address table
        try:
            new_address = Address(
                street_name=entry.get(kwargs.get('street_name')),
                post_code=int(entry.get(kwargs.get('post_code'))),
                post_area=entry.get(kwargs.get('post_area')),
            )
            session.add(new_address)
        except ValueError:
            pass
        if (time() - time1) >= last_output:
            last_output += output_interval
            print('{:0.1f}% done.'.format(
                (idx) / len(data) * 100
            ))
    print('Saving all entries to database')
    session.commit()
    print('Done')


def json_to_db(json_file, **kwargs):
    """Retrieve all entries in a json-file and add it to db.."""
    with open(json_file) as data_file:
        address_data = json.load(data_file)
    populate_db(address_data, **kwargs)


if __name__ == "__main__":
    if "--setup" in sys.argv:
        print('Dropping and reacreating database')
        session.close_all()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        json_to_db(
            'data/adresser.json',
            street_name='vei',
            post_code='postnummer',
            post_area='postnummeromrade'
        )
