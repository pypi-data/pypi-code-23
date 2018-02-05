import vcr as _vcr

# chipmunk parameters for test data
x = -2094585
y = 1952805
x_nodata = -183585.0
y_nodata = 302805.0
acquired = '2010/2013'
profile = 'chipmunk-ard'
env = {'CHIPMUNK_URL': 'http://localhost:5656'}
cassette = 'test/resources/chipmunk-ard-v1-cassette.yaml'
vcr = _vcr.VCR(record_mode='new_episodes')
