"""Retrieval-functions for getting address-data from database"""
import re

from norwegian_adresses.model_pymongo import collection
from norwegian_adresses.stupid_road_names import stupid_road_names

remove_house_number = re.compile(r'\s\d{0,3}\w$', re.IGNORECASE)


def address_to_dict(address):
    """Converts an address object to a regular dictionary."""
    d = {i: address[i] for i in address if i not in [
        'street_name_lc', 'place_lc', '_id']}
    d['id'] = str(address['_id'])
    return d


class NorAddress(object):
    """Class for searching norwegian addresses from MongoDB."""

    def __init__(self, as_dict=True):
        self.as_dict = as_dict

    def by_post_code(self, post_code, as_dict=None):
        """Return the post-area for a postcode."""
        as_dict = self.as_dict if as_dict is None else as_dict

        address = collection.find_one({
            'post_code': post_code
        })
        if address:
            return address_to_dict(address) if as_dict else address
        else:
            raise ValueError(
                'Did not find an address matching {}'.format(post_code))

    def post_codes_by_post_area(self, post_area, as_dict=None):
        """Return the post-code for a post-area."""
        as_dict = self.as_dict if as_dict is None else as_dict

        post_codes = collection.find(
            {
                'post_area':
                    {
                        '$regex': "^" + post_area,
                        '$options': 'i'
                    }
            },
            {
                'post_code': 1
            }
        ).distinct('post_code')
        if post_codes:
            return post_codes
        else:
            raise ValueError(
                'Did not find an address matching {}'.format(post_area))

    def by_street_name(self, street_name_with_house_number, post_code, as_dict=None):
        """Return a addres from a street_name (ignoring housenumber)."""
        as_dict = self.as_dict if as_dict is None else as_dict

        street_name = filter_out_housenumber_from_street_name(
            street_name_with_house_number)
        address = collection.find_one(
            {
                'street_name_lc': street_name,
                'post_code': post_code,
            }
        )
        if address:
            if as_dict:
                return address_to_dict(address)
            return address

    def by_street_name_closest_to(
            self,
            street_name,
            contains=True,
            near_post_code=0,
            near_geo=None,
            limit=10,
            as_dict=None
    ):
        """
        Return the post-code for a street_name.

        street_name: the street to lookup e.g. Kings Road
        contains: default to True, to do partial matches. False for strict matches
        near_post_code: provide a post_code, and will order by closest to.
        limit: default to 10. Max entries to retrieve. use None to get all.
        """
        as_dict = self.as_dict if as_dict is None else as_dict

        if contains:
            if near_geo:
                addresses = collection.find(
                    {
                        'street_name_lc': {'$regex': "^" + street_name,
                                           '$options': 'i'},
                        "loc": {
                            "$near": near_geo
                        }
                    }
                ).limit(10)
                if as_dict:
                    return [address_to_dict(x) for x in addresses]
                return addresses
            else:
                addresses = collection.aggregate([
                    {'$match': {'street_name_lc': {'$regex': "^" + street_name,
                                                   '$options': 'i'}}},
                    {'$project': {'diff': {'$abs': {'$subtract': [
                        near_post_code, '$post_code']}}, 'doc': '$$ROOT'}},
                    {'$sort': {'diff': 1}},
                    {'$limit': limit},
                ])
            formated_adresses = []
            for address in addresses:
                formated_adresses.append(address['doc'])
            addresses = formated_adresses
        else:
            addresses = collection.find(
                {
                    'street_name_lc': street_name
                },
                {
                    '_id': 0
                }
            )
        if addresses:
            if as_dict:
                return [address_to_dict(x) for x in addresses]
            return addresses
        else:
            raise ValueError(
                'Did not find an address matching {}'.format(street_name))




def filter_out_housenumber_from_street_name(street_name_with_house_number):
    """Return a street_name without a housenumber."""
    street_name_with_house_number = street_name_with_house_number.strip().lower()
    if street_name_with_house_number in stupid_road_names:
        return street_name_with_house_number
    return re.sub(remove_house_number, '', street_name_with_house_number)

def generate_list_of_stupid_road_names():
    """This is a list of problematic road names."""
    addresses = collection.find(
        {
            'street_name_lc': {'$regex': r"\s\d{1,4}$",
                               '$options': 'i'},
        }
    )
    d = []
    for p in addresses:
        d.append(p.get('street_name'))

    return d
