"""Retrieval-functions for getting address-data from database"""
import re

if __name__ == '__main__':
    from model_pymongo import collection
    from stupid_road_names import stupid_road_names
else:
    from .model_pymongo import collection
    from .stupid_road_names import stupid_road_names

remove_house_number = re.compile(r'\s\d{0,3}\w$', re.IGNORECASE)

def address_to_dict(address):
    d = {i:address[i] for i in address if i not in ['street_name_lc', 'place_lc', '_id']}
    d['id'] = str(address['_id'])
    return d

def get_post_area_for_post_code(post_code):
    """Return the post-area for a postcode."""
    address = collection.find_one({
        'post_code': post_code
    })
    if address:
        return address.get("post_area")
    else:
        raise ValueError(
            'Did not find an address matching {}'.format(post_code))


def get_post_code_for_post_area(post_area, as_dict=True):
    """Return the post-code for a post-area."""
    addresses = collection.find(
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
    if addresses:
        if as_dict:
            return [address_to_dict(x) for x in addresses]
        return addresses
    else:
        raise ValueError(
            'Did not find an address matching {}'.format(post_area))


def filter_out_housenumber_from_street_name(street_name_with_house_number):
    """Return a street_name without a housenumber."""
    street_name_with_house_number = street_name_with_house_number.strip().lower()
    if street_name_with_house_number in stupid_road_names:
        return street_name_with_house_number
    return re.sub(remove_house_number, '', street_name_with_house_number)


def get_location_from_address(street_name_with_house_number, post_code, as_dict=True):
    """Return a geolocation from a street_name (ignoring housenumber)."""
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


def get_address_from_street_name(
        street_name,
        contains=True,
        near_post_code=0,
        near_geo=None,
        limit=10,
        as_dict=True
):
    """
    Return the post-code for a street_name.

    street_name: the street to lookup e.g. Kings Road
    contains: default to True, to do partial matches. False for strict matches
    near_post_code: provide a post_code, and will order by closest to.
    limit: default to 10. Max entries to retrieve. use None to get all.
    """
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
                # {'$project': {
                #     'diff': 0,
                #     '_id': 0,
                #     'doc': {
                #         '_id': 0
                #     }
                # }},
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

if __name__ == '__main__':
    result = get_location_from_address('Kongens gate 122b', 4610)
    print(result)
    # print(generate_list_of_stupid_road_names())
