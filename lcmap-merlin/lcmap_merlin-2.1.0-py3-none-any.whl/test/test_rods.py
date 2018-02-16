from cytoolz import first
from cytoolz import second
from merlin import cfg
from merlin import chips
from merlin import dates
from merlin import functions as f
from merlin import specs
from merlin import rods
from functools import reduce
import numpy as np
import test
 
 
def test_from_chips():
    chips = list()
    chips.append({'data': np.int_([[11, 12, 13],
                                   [14, 15, 16],
                                   [17, 18, 19]])})
    chips.append({'data': np.int_([[21, 22, 23],
                                   [24, 25, 26],
                                   [27, 28, 29]])})
    chips.append({'data': np.int_([[31, 32, 33],
                                   [34, 35, 36],
                                   [37, 38, 39]])})
    pillar = rods.from_chips(chips)
    assert pillar.shape[0] == chips[0]['data'].shape[0]
    assert pillar.shape[1] == chips[0]['data'].shape[1]
    assert pillar.shape[2] == len(chips)

    # going to flatten both the chips arrays and the pillar array
    # then perform black magic and verify that the values wound up
    # where they belonged in the array positions.
    # using old style imperative code as double insurance
    # happiness is not doing this and relying on functional principles only
    # because direct manipulation of memory locations is error prone and
    # very difficult to think about.
    # We're mapping array locations between two things that look like this:
    # [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27 ...]
    # [11, 21, 31, 12, 22, 32, 13, 23, 33, 14, 24, 34, 15, 25, 35, 16, 26 ...]
    # This alone should serve as all the evidence needed to prove that
    # imperative programming is bad for everyone involved.  I am very sorry.
    fchips = list(f.flatten([c['data'].flatten() for c in chips]))
    jump = reduce(lambda accum, v: accum + v, pillar.shape) # 9
    modulus = pillar.shape[0] # 3
    for i, val in enumerate(pillar.flatten()):
        factor = i % modulus # 0 1 2
        group = i // modulus # 0 1 2
        assert val == fchips[(factor * jump) + group]


def test_locate():
    # test data.  sum(locs) + 2 should equal sum(rods) per inner array
    # value of sum of every inner array element should be unique.
    _locs = np.int_([[[0, 0], [0, 1], [0, 2]],
                     [[1, 3], [1, 4], [1, 5]],
                     [[2, 6], [2, 7], [2, 8]]])

    _rods = np.int_([[[0, 0, 2], [0, 0, 3], [0, 0, 4]],
                     [[1, 0, 5], [1, 0, 6], [1, 0, 7]],
                     [[2, 0, 8], [2, 0, 9], [2, 0, 10]]])

    # sanity check
    locs_total = _locs.reshape(9, 2).sum(axis=1) + 2
    rods_total = _rods.reshape(9, 3).sum(axis=1)
    assert np.array_equal(locs_total, rods_total)

    # make sure we located all the rods correctly.
    flatlocs = _locs.reshape(9, 2)
    tseries = rods.locate(locations=_locs, rods=_rods)
    assert all([tseries[tuple(loc)].sum() == loc.sum() + 2 for loc in flatlocs])


@test.vcr.use_cassette(test.cassette)
def test_create():
 
    c = cfg.get('chipmunk-ard', env=test.env)
 
    x, y = c.get('snap_fn')(x=test.x, y=test.y).get('chip').get('proj-pt')

    ubids = cfg.ubids.get('chipmunk-ard').get('reds')

    registry = c.get('registry_fn')()
    
    refspec = specs.refspec(specs.mapped(specs=registry, ubids={'reds': ubids}))
    # print("REFSPEC:{}".format(refspec))
 
    chipseq = c.get('chips_fn')(x=x,
                                y=y,
                                acquired=test.acquired,
                                ubids=ubids)

    dateseq = dates.mapped(chipmap=dict(reds=chipseq)).get('reds')

    grid = {x['name']: x for x in c.get('grid_fn')()}.get('chip')
 
    locations = chips.locations(x=x,
                                y=y,
                                cw=first(refspec.get('data_shape')),
                                ch=second(refspec.get('data_shape')),
                                rx=grid.get('rx'),
                                ry=grid.get('ry'),
                                sx=grid.get('sx'),
                                sy=grid.get('sy'))

    _rods = rods.create(x=x,
                        y=y,
                        chipseq=chipseq,
                        dateseq=dateseq,
                        locations=locations,
                        spec_index=specs.index(registry))

    assert len(_rods) == 10000
    assert type(_rods) is dict
