from cytoolz import filter
from cytoolz import first
from cytoolz import get_in
from cytoolz import partial
from merlin import cfg
from merlin import chipmunk
from merlin import chips
from merlin import dates
from merlin import files
from merlin import formats
from merlin import functions
from merlin import rods
from merlin import specs


def create(x, y, acquired, cfg):
    """Create a timeseries.

    Args:
        x (int): x coordinate
        y (int): y coordinate
        acquired (string): iso8601 date range
        cfg (dict): A Merlin configuration

    Returns:
        tuple - Results of format_fn applied to results of chips_fn
    """
    
    x, y = get_in(['chip', 'proj-pt'], cfg['snap_fn'](x=x, y=y))

    # get specs
    specmap = cfg['specs_fn'](specs=cfg['registry_fn']())

    # get function that will return chipmap.
    # Don't create state with a realized variable to preserve memory
    chipmap = partial(chips.mapped,
                      x=x,
                      y=y,
                      acquired=acquired,
                      specmap=specmap,
                      chips_fn=cfg['chips_fn'])

    # calculate locations chip.  There's another function
    # here to be split out and organized.
    
    grid = first(filter(lambda x: x['name'] == 'chip',
                        cfg['grid_fn']()))

    cw, ch = specs.refspec(specmap).get('data_shape')
    
    locations = partial(chips.locations,
                        x=x,
                        y=y,
                        cw=cw,
                        ch=ch,
                        rx=grid.get('rx'),
                        ry=grid.get('ry'),
                        sx=grid.get('sx'),
                        sy=grid.get('sy'))
    
    return cfg['format_fn'](x=x,
                            y=y,
                            locations=locations(),
                            dates_fn=cfg['dates_fn'],
                            specmap=specmap,
                            chipmap=chipmap()) 
