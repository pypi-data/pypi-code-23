"""Chipmunk.py is the interface module to Chipmunk for Merlin.

Any functions chipmunk exposes are represented here as defined.

New abstractions or higher level abstractions should be created
in modules that import chipmunk.py.  For maximum flexibility do not
import chipmunk.py directly... inject it via a kernel or DI construct.  

Multi-version support: 
To support multiple versions of Chipmunk create new modules that correspond to
the appropriate version number.
"""

from cytoolz import reduce
from functools import partial
from operator import add
import requests


def chips(x, y, acquired, ubids, url, resource='/chips'):
    """Returns chips from a Chipmunk url given x, y, date range and ubid sequence

    Args:
        x (int): projection coordinate x
        y (int): projection coordinate y
        acquired (str): ISO8601 daterange '2012-01-01/2014-01-03'
        ubids (sequence): sequence of ubids
        url (str): protocol://host:port/path
        resource (str): /chips/resource/path (default: /chips)

    Returns:
        tuple: chips

    Example:
        >>> chipmunk.chips(url='http://host:port/path',
                           x=123456,
                           y=789456,
                           acquired='2012-01-01/2014-01-03',
                           ubids=['LE07_SRB1', 'LT05_SRB1'])
        (LE07_SRB1_DATE1, LT05_SRB1_DATE2, LE07_SRB1_DATE2, ...)
    """

    url = '{}{}'.format(url, resource)
    params = [{'x': x, 'y': y, 'acquired': acquired, 'ubid': u } for u in ubids]

    # check to see if there were results.  If yes return .json() else [{}]
    responses = [requests.get(url=url, params=p).json() for p in params]
    return tuple(reduce(add, responses))


def registry(url, resource='/registry'):
    """Retrieve the chip spec registry

    Args:
        url (str): protocol://host:port/path
        resource (str): /registry/resource/path (default: /registry)

    Returns:
        list

    Example:
        >>> chipmunk.registry(url='http://host:port/path')
         [{'data_fill': '-9999',
           'data_mask': {},
           'data_range': [],
           'data_scale': None,
           'data_shape': [100, 100],
           'data_type': 'INT16',
           'data_units': None,
           'info': 'band 5 top-of-atmosphere reflectance',
           'tags': ['swir1', 'b5', 'tab5', 'lt05', 'lt05_tab5', 'ta'],
           'ubid': 'LT05_TAB5'},
          {'data_fill': '-9999',
           'data_mask': {},
           'data_range': [],
           'data_scale': None,
           'data_shape': [100, 100],
           'data_type': 'INT16',
           'data_units': None,
           'info': 'band 7 top-of-atmosphere reflectance',
           'tags': ['lt05_tab7', 'b7', 'lt05', 'swir2', 'tab7', 'ta'],
           'ubid': 'LT05_TAB7'}, ...]
    """
    
    return requests.get(url="{}{}".format(url, resource)).json()


def grid(url, resource='/grid'):
    """Determine the chip and tile coordinates for a point.
  
    Args:
        url (str): protocol://host:port/path
        resource (str): /grid/snap/resource (default: /grid/snap)
 
    Returns:
        dict

    Example:
        >>> chipmunk.grid(url='http://host:port/path)
        [{"name":"tile",
          "proj":null,
          "rx":1.0,
          "ry":-1.0,
          "sx":150000.0,
          "sy":150000.0,
          "tx":2565585.0,
          "ty":3314805.0},
         {"name":"chip",
          "proj":null,
          "rx":1.0,
          "ry":-1.0,
          "sx":3000.0,
          "sy":3000.0,
          "tx":2565585.0,
          "ty":3314805.0}]
    """
    
    url = '{}{}'.format(url, resource)
    return requests.get(url=url).json()


def snap(x, y, url, resource='/grid/snap'):
    """Determine the chip and tile coordinates for a point.
  
    Args:
        x (int): projection coordinate x
        y (int): projection coordinate y
        url (str): protocol://host:port/path
        resource (str): /grid/snap/resource (default: /grid/snap)
 
    Returns:
        dict

    Example:
        >>> chipmunk.snap(x=0, y=0, url='http://host:port/path')
         {'chip': {'grid-pt': [855.0, 1104.0], 'proj-pt': [-585.0, 2805.0]},
          'tile': {'grid-pt': [17.0, 22.0], 'proj-pt': [-15585.0, 14805.0]}}
    """
    
    url = '{}{}'.format(url, resource)
    return requests.get(url=url, params={'x': x, 'y': y}).json()


def near(x, y, url, resource='/grid/near'):
    """Determines chips and tiles that lie a point

    Args:
        x (int): projection coordinate x
        y (int): projection coordinate y
        url (str): protocol://host:port/path
        resource (str): /grid/near/resource (default: /grid/near)
    
    Returns:
        dict

    Example:
        >>> chipmunk.near(x=0, y=0, url='http://host:port/path')
        {'chip': [{'grid-pt': [854.0, 1105.0], 'proj-pt': [-3585.0, -195.0]},
                  {'grid-pt': [854.0, 1104.0], 'proj-pt': [-3585.0, 2805.0]},
                  {'grid-pt': [854.0, 1103.0], 'proj-pt': [-3585.0, 5805.0]},
                  {'grid-pt': [855.0, 1105.0], 'proj-pt': [-585.0, -195.0]},
                  {'grid-pt': [855.0, 1104.0], 'proj-pt': [-585.0, 2805.0]},
                  {'grid-pt': [855.0, 1103.0], 'proj-pt': [-585.0, 5805.0]},
                  {'grid-pt': [856.0, 1105.0], 'proj-pt': [2415.0, -195.0]},
                  {'grid-pt': [856.0, 1104.0], 'proj-pt': [2415.0, 2805.0]},
                  {'grid-pt': [856.0, 1103.0], 'proj-pt': [2415.0, 5805.0]}],
         'tile': [{'grid-pt': [16.0, 23.0], 'proj-pt': [-165585.0, -135195.0]},
                  {'grid-pt': [16.0, 22.0], 'proj-pt': [-165585.0, 14805.0]},
                  {'grid-pt': [16.0, 21.0], 'proj-pt': [-165585.0, 164805.0]},
                  {'grid-pt': [17.0, 23.0], 'proj-pt': [-15585.0, -135195.0]},
                  {'grid-pt': [17.0, 22.0], 'proj-pt': [-15585.0, 14805.0]},
                  {'grid-pt': [17.0, 21.0], 'proj-pt': [-15585.0, 164805.0]},
                  {'grid-pt': [18.0, 23.0], 'proj-pt': [134415.0, -135195.0]},
                  {'grid-pt': [18.0, 22.0], 'proj-pt': [134415.0, 14805.0]},
                  {'grid-pt': [18.0, 21.0], 'proj-pt': [134415.0, 164805.0]}]}
    """
    
    url = '{}{}'.format(url, resource)
    return requests.get(url=url, params={'x': x, 'y': y}).json()
