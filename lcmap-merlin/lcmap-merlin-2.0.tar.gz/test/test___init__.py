from cytoolz import first
from cytoolz import last
from cytoolz import partial
from cytoolz import sliding_window
from merlin import cfg
from merlin import chips
from merlin import create
from merlin import specs
from operator import eq
from operator import gt
import numpy as np
import test

@test.vcr.use_cassette(test.cassette)    
def test_create_nodata():
    _cfg = cfg.get(profile=test.profile, env=test.env)
    data = create(x=test.x_nodata, y=test.y_nodata, acquired=test.acquired, cfg=_cfg)
    assert len(data) == 0
    assert type(data) is tuple

    
@test.vcr.use_cassette(test.cassette)    
def test_create():
    # data should be shaped: ( ((chip_x, chip_y, x1, y1),{}),
    #                          ((chip_x, chip_y, x1, y2),{}), )

    _cfg = cfg.get(profile=test.profile, env=test.env)    
    data = create(x=test.x, y=test.y, acquired=test.acquired, cfg=_cfg)

    # make sure we have 10000 results and the response structure
    assert len(data) == 10000
    assert isinstance(data, tuple)
    assert isinstance(data[0], tuple)
    assert isinstance(data[0][0], tuple)
    assert isinstance(data[0][1], dict)

    # check key length: chip_x, chip_y, x, y.
    assert len(data[0][0]) == 4

    # check to make sure we have equal length values and that the values
    # are not empty.  FYI -- only spot checking the first returned result
    lens = [len(data[0][1][key]) for key in data[0][1]]
    assert all([eq(*x) for x in sliding_window(2, lens)]) == True

    # make sure everything isn't zero length
    assert all([gt(x, 0) for x in lens]) == True


@test.vcr.use_cassette(test.cassette)
def test_compare_timeseries_to_chip():
    # Make sure the timeseries values match the most recent chip for a spectra.
    # This will validate the chip was not transposed during timeseries creation.
    
    _cfg =   cfg.get(profile=test.profile, env=test.env)
    _ubids = cfg.ubids.get(test.profile).get('reds')
    _chips = _cfg.get('chips_fn')(x=test.x, y=test.y, acquired=test.acquired, ubids=_ubids)
    _index = specs.index(_cfg.get('registry_fn')())
     
    most_recent_chip = last(sorted(_chips, key=lambda d: d['acquired']))
    most_recent_chip = first(chips.to_numpy(spec_index=_index, chips=[most_recent_chip]))

    time_series = create(x=test.x, y=test.y, acquired=test.acquired, cfg=_cfg)
                         
    # this is a 2d 100x100 array of values arranged spatially
    chip_data = most_recent_chip['data']

    # reconstruct a 2d 100x100 array of values from the most recent observation in the time series.  Idea here is it
    # should match the chip_data
    #.reshape(100, 100)
    def observation(record):
        # return x, y, value for the most recent observation in the time series
        return {'x': record[0][2], 'y': record[0][3], 'v': record[1]['reds'][0]}
        
    def lookups(values):
        # need to know the array position of each value, be able to look them up
        # this is a coordinate space to array space mapping
        return  {v:i for i,v in enumerate(values)}

    def build_array(obs, x_lookups, y_lookups):
        # takes all the observations and the x/y lookup tables, returns an ndarray (float)

        # initialze an ndarray that matches the dimensions of x and y
        ar = np.zeros([len(x_lookups), len(y_lookups)], dtype=np.float)

        # populate the ndarray
        for o in obs:
            x = x_lookups.get(o['x'])
            y = y_lookups.get(o['y'])
            ar.itemset((y, x), o.get('v'))
            
        return ar
       
    observations = list(map(observation, time_series))
    xset = sorted(list(set(map(lambda a: a['x'], observations))))
    yset = sorted(list(set(map(lambda a: a['y'], observations))), reverse=True)
    suspect_data = build_array(obs=observations,
                               x_lookups=lookups(xset),
                               y_lookups=lookups(yset))

    assert np.array_equal(suspect_data, chip_data)
