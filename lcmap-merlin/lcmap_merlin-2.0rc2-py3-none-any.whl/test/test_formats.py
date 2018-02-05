from cytoolz import first
from cytoolz import get_in
from cytoolz import partial
from cytoolz import second
from merlin import cfg
from merlin import chips
from merlin import specs
from merlin.formats import pyccd
import test


@test.vcr.use_cassette(test.cassette)
def test_pyccd():
    c = cfg.get('chipmunk-ard', env=test.env)
    
    x, y = get_in(['chip', 'proj-pt'], c['snap_fn'](x=test.x, y=test.y))

    # get specs
    specmap = c['specs_fn'](specs=c['registry_fn']())

    # get function that will return chipmap.
    # Don't create state with a realized variable to preserve memory
    chipmap = partial(chips.mapped,
                      x=test.x,
                      y=test.y,
                      acquired=test.acquired,
                      specmap=specmap,
                      chips_fn=c['chips_fn'])

    # calculate locations chip.  There's another function
    # here to be split out and organized.
    
    grid = first(filter(lambda x: x['name'] == 'chip',
                        c['grid_fn']()))

    cw, ch = specs.refspec(specmap).get('data_shape')
    
    locations = chips.locations(x=x,
                                y=y,
                                cw=cw,
                                ch=ch,
                                rx=grid.get('rx'),
                                ry=grid.get('ry'),
                                sx=grid.get('sx'),
                                sy=grid.get('sy'))
    
    data = c['format_fn'](x=x,
                          y=y,
                          locations=locations,
                          dates_fn=c['dates_fn'],
                          specmap=specmap,
                          chipmap=chipmap()) 

    # we are only testing the structure of the response here.
    # Full data validation is being done in the test for merlin.create()
    assert type(data) is tuple
    assert len(data) == 10000
    assert type(first(data)) is tuple
    assert type(first(first(data))) is tuple
    assert type(second(first(data))) is dict
    assert type(second(second(first(data)))) is tuple or list
    assert len(second(second(first(data)))) > 0
