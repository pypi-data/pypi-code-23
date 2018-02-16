from base64 import b64decode
from cytoolz import drop
from cytoolz import first
from cytoolz import get_in
from cytoolz import reduce
from cytoolz import unique
from merlin import functions as f
from merlin import specs
from operator import add
import logging
import numpy as np
import requests

logger = logging.getLogger(__name__)


def locations(x, y, cw, ch, rx, ry, sx, sy):
    """Computes locations for array elements that fall within the shape
    specified by chip_spec['data_shape'] using the x & y as the origin.  
    locations() does not snap() x & y... this
    should be done prior to calling locations() if needed.

    Args:
        x: x coordinate
        y: y coordinate
        cw: chip width in pixels (e.g. 100 pixels)
        ch: chip height in pixels (e.g. 100 pixels)
        rx: x reflection (e.g. 1)
        ry: y reflection (e.g. -1)
        sx: x scale (e.g. 3000 meters)
        sy: y scale (e.g. 3000 meters)
    Returns:
        a two (three) dimensional numpy array of [x, y] coordinates
    """

    pw = (sx * rx) / cw # e.g. 30 meters
    ph = (sy * ry) / ch # e.g. -30 meters
    
    # determine ends
    endx = x + cw * pw
    endy = y + ch * ph

    #################################################
    # WARNING: The following line would transpose the
    # resulting matrix by 90 degrees.  In order to
    # generate the proper row major matrix the order
    # y and x are created inside mgrid matters
    #
    # x, y = np.mgrid[x:endx:pw, y:endy:ph]
    #################################################
    
    # build arrays of end - start / step shape
    # flatten into 1d, concatenate and reshape to fit chip
    _y, _x = np.mgrid[y:endy:ph, x:endx:pw]
    matrix = np.c_[_x.ravel(), _y.ravel()]
    return np.reshape(matrix, (cw, ch, 2))


def dates(chips):
    """Dates for a sequence of chips

    Args:
        chips: sequence of chips

    Returns:
        tuple: datestrings
    """

    return tuple([c['acquired'] for c in chips])


def trim(chips, dates):
    """Eliminates chips that are not from the specified dates

    Args:
        chips: Sequence of chips
        dates: Sequence of dates that should be included in result

    Returns:
        tuple: filtered chips
    """

    return tuple(filter(lambda c: c['acquired'] in dates, chips))


def chip_to_numpy(chip, chip_spec):
    """Removes base64 encoding of chip data and converts it to a numpy array

    Args:
        chip: A chip
        chip_spec: Corresponding chip_spec

    Returns:
        a decoded chip with data as a shaped numpy array
    """
    
    shape = chip_spec['data_shape']
    dtype = chip_spec['data_type'].lower()
    cdata = b64decode(chip['data'])

    chip['data'] = np.frombuffer(cdata, dtype).reshape(*shape)
    return chip


def to_numpy(chips, spec_index):
    """Converts the data for a sequence of chips to numpy arrays

    Args:
        chips (sequence): a sequence of chips
        spec_index (dict): chip_specs keyed by ubid

    Returns:
        sequence: chips with data as numpy arrays
    """

    return map(lambda c: chip_to_numpy(c, spec_index[c['ubid']]), chips)


def identity(chip):
    """Determine the identity of a chip.

    Args:
        chip (dict): A chip

    Returns:
        tuple: Tuple of the chip identity field
    """

    return tuple([chip['x'], chip['y'],
                  chip['ubid'], chip['acquired']])


def deduplicate(chips):
    """Accepts a sequence of chips and returns a sequence of chips minus
    any duplicates.  A chip is considered a duplicate if it shares an x, y, UBID
    and acquired date with another chip.

    Args:
        chips (sequence): Sequence of chips

    Returns:
        tuple: A nonduplicated tuple of chips
    """

    return tuple(unique(chips, key=identity))


def mapped(x, y, acquired, specmap, chips_fn):
    """Maps chips_fn results to keys from specmap.

    Args:
        x (int): x coordinate
        y (int): y coordinate
        acquired (str): iso8601 date range 
        specmap (dict): map of specs
        chips_fn (fn): function to return chips

    Returns:
        dict: {k: chips_fn()}

    """
    
    return {k: chips_fn(x=x, y=y, acquired=acquired, ubids=specs.ubids(v)) for k, v in specmap.items()}


def rsort(chips, key=lambda c: c['acquired']):
    """Reverse sorts a sequence of chips by date.

    Args:
        chips: sequence of chips

    Returns:
        sorted sequence of chips
    """

    return tuple(f.rsort(chips, key=key))
