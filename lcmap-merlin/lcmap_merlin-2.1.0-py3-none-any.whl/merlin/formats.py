from cytoolz import merge
from cytoolz import partial
from merlin import chips
from merlin import dates
from merlin import functions
from merlin import rods
from merlin import specs


def pyccd(x, y, locations, dates_fn, specmap, chipmap):
    """Builds inputs for the pyccd algorithm.

    Args:
        x: x projection coordinate of chip
        y: y projection coordinate of chip
        locations: chip shaped 2d array of projection coordinates
        dates_fn (fn): returns dates that should be included in time series
        specmap (dict): mapping of keys to specs
        chipmap (dict): mapping of keys to chips

    Returns:
        A tuple of tuples.

    The pyccd format key is ```(chip_x, chip_y, x, y)``` with a
    dictionary of sorted numpy arrays representing each spectra plus an
    additional sorted dates array.

    >>> pyccd_format(*args)
        (((chip_x, chip_y, x1, y1), {"dates":  [],  "reds": [],
                                     "greens": [],  "blues": [],
                                     "nirs1":  [],  "swir1s": [],
                                     "swir2s": [],  "thermals": [],
                                     "qas":    []}),
         ((chip_x, chip_y, x1, y2), {"dates":  [],  "reds": [],
                                     "greens": [],  "blues": [],
                                     "nirs1":  [],  "swir1s": [],
                                     "swir2s": [],  "thermals": [],
                                     "qas":    []}))
        ...
    """
    
    _index   = specs.index(list(functions.flatten(specmap.values())))
    _dates   = dates_fn(datemap=dates.mapped(chipmap))
    _creator = partial(rods.create, x=x, y=y, dateseq=_dates, locations=locations, spec_index=_index)
    _flipped = partial(functions.flip_keys, {k: _creator(chipseq=v) for k, v in chipmap.items()})
    
    _rods = functions.insert_into_every(key='dates',
                                        value=list(map(dates.to_ordinal, dates.rsort(_dates))),
                                        dods=_flipped())
                                 
    return tuple((k, v) for k, v in _rods.items())


