"""Retrieval-functions for getting address-data from database"""
from sqlalchemy import func

from model import Address, AddressQuery, session


def get_post_area_for_post_code(post_code):
    """Return the post-area for a postcode."""
    address = AddressQuery.filter_by(
        post_code=post_code
    ).first()
    if address:
        return address.post_area
    else:
        raise ValueError(
            'Did not find an address matching {}'.format(post_code))


def get_post_code_for_post_area(post_area):
    """Return the post-code for a post-area."""
    addresses = session.query(Address.post_code).filter(
        Address.post_area.ilike(post_area)
    ).group_by(
        Address.post_code
    ).all()
    if addresses:
        post_codes = []
        for address in addresses:
            post_codes.append(address.post_code)
        return post_codes
    else:
        raise ValueError(
            'Did not find an address matching {}'.format(post_area))


def get_address_from_street_name(
        street_name,
        contains=True,
        near_post_code=None,
        limit=10
):
    """
    Return the post-code for a street_name.

    street_name: the street to lookup e.g. Kings Road
    contains: default to True, to do partial matches. False for strict matches
    near_post_code: provide a post_code, and will order by closest to.
    limit: default to 10. Max entries to retrieve. use None to get all.
    """
    query = AddressQuery
    if contains:
        query = query\
            .filter(
                func.upper(Address.street_name)
                .contains(func.upper(street_name))
            )
    else:
        query = query\
            .filter(
                Address.street_name.ilike(street_name)
            )
    if near_post_code:
        query = query.order_by(
            func.abs(Address.post_code - near_post_code)
        )
    if limit:
        addresses = query.limit(limit)
    addresses = query.all()
    if addresses:
        return addresses
    else:
        raise ValueError(
            'Did not find an address matching {}'.format(street_name))

if __name__ == '__main__':
    known_values_street_name = {
        'Kongens gate':
            [{
                'post_code': 4633,
                'post_area': 'KRISTIANSAND S'
            }],
        'Bergtoras vei':
            [{
                'post_code': 4633,
                'post_area': 'KRISTIANSAND S'
            }],
        'Justnesveien':
            [{
                'post_code': 4633,
                'post_area': 'KRISTIANSAND S'
            }],
    }
    for key, value in known_values_street_name.items():
        results = get_address_from_street_name(key)
        parsed_result = {}
        for result in results:
            if key not in parsed_result:
                parsed_result[key] = []
            parsed_result[key].append({
                'post_code': result.post_code,
                'post_area': result.post_area
            })

        print(parsed_result)
        # self.assertCountEqual(parsed_result, value)
