from cytoolz import concat
from cytoolz import first
from cytoolz import identity
from merlin import cfg
from merlin import chipmunk
import test

@test.vcr.use_cassette(test.cassette)
def test_chips():
    red_chips = chipmunk.chips(x=test.x,
                               y=test.y,
                               acquired=test.acquired,
                               ubids=cfg.ubids.get('chipmunk-ard').get('reds'),
                               url=test.env.get('CHIPMUNK_URL'))
    assert len(red_chips) > 0
    assert type(red_chips) is tuple
    

@test.vcr.use_cassette(test.cassette)
def test_registry():

    registry = chipmunk.registry(url=test.env.get('CHIPMUNK_URL'))
    assert len(registry) > 0
    assert type(registry) is tuple or list

    entry = first(registry)
    assert type(entry) is dict

    keys = ['ubid', 'info', 'tags', 'data_type', 'data_fill', 'data_shape']
    assert all([key in entry for entry in registry for key in keys])
    

@test.vcr.use_cassette(test.cassette)
def test_grid():
    grid = chipmunk.grid(url=test.env.get('CHIPMUNK_URL'))
    assert len(grid) == 2
    assert type(grid) is list or tuple
    assert set(['chip', 'tile']) == set([g.get('name') for g in grid])

    keys = ['proj', 'rx', 'ry', 'sx', 'sy', 'tx', 'ty']
    assert all([key in g for g in grid for key in keys])
    

@test.vcr.use_cassette(test.cassette)
def test_snap():
    snapped = chipmunk.snap(x=test.x,
                            y=test.y,
                            url=test.env.get('CHIPMUNK_URL'))
    
    assert type(snapped) is dict
    assert len(snapped) is 2
    
    keys = ['chip', 'tile']
    assert all([key in snapped for key in keys])

    subkeys = ['grid-pt', 'proj-pt']
    assert all([subkey in v for k, v in snapped.items() for subkey in subkeys])


@test.vcr.use_cassette(test.cassette)
def test_near():
    near = chipmunk.near(x=test.x,
                         y=test.y,
                         url=test.env.get('CHIPMUNK_URL'))
    
    assert type(near) is dict

    assert len(near) is 2
    
    keys = ['chip', 'tile']

    assert all([key in near for key in keys])

    assert all([len(near[key]) is 9 for key in keys])

    assert all([type(near[key]) is list or tuple for key in keys])
    
    assert all(map(lambda key: key in near, keys))

    assert all(map(lambda sub: type(sub) is list or tuple, map(lambda key: near[key], keys)))

    assert all(list(map(lambda entry: 'grid-pt' in entry and 'proj-pt' in entry,
                        concat(map(lambda key: near[key], keys)))))
    
 
