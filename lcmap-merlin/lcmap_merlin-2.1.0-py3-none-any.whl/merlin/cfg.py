from cytoolz import assoc
from cytoolz import merge
from functools import partial
from merlin import chipmunk
from merlin import chips
from merlin import dates
from merlin import formats
from merlin import specs
import os


ubids = {'chipmunk-ard': {'reds':     ['LC08_SRB4',    'LE07_SRB3',    'LT05_SRB3',    'LT04_SRB3'],
                          'greens':   ['LC08_SRB3',    'LE07_SRB2',    'LT05_SRB2',    'LT04_SRB2'],
                          'blues':    ['LC08_SRB2',    'LE07_SRB1',    'LT05_SRB1',    'LT04_SRB1'],
                          'nirs':     ['LC08_SRB5',    'LE07_SRB4',    'LT05_SRB4',    'LT04_SRB4'],
                          'swir1s':   ['LC08_SRB6',    'LE07_SRB5',    'LT05_SRB5',    'LT04_SRB5'],
                          'swir2s':   ['LC08_SRB7',    'LE07_SRB7',    'LT05_SRB7',    'LT04_SRB7'],
                          'thermals': ['LC08_BTB10',   'LE07_BTB6',    'LT05_BTB6',    'LT04_BTB6'],
                          'qas':      ['LC08_PIXELQA', 'LE07_PIXELQA', 'LT05_PIXELQA', 'LT04_PIXELQA']},
         'chipmunk-aux': {'trends':  ['AUX_TRENDS'],
                          'posidex': ['AUX_POSIDEX'],
                          'mpw':     ['AUX_MPW'],
                          'aspect':  ['AUX_ASPECT'],
                          'slope':   ['AUX_SLOPE'],
                          'dem':     ['AUX_DEM']}}


def profiles(env, profile=None):
    """Retrieve a configuration profile with env applied.

    Args:
        env (dict): Environment variables
        profile (str): Name of profile to load.  If no profile is supplied all profiles
                        are returned.

    Returns:
        dict: Profile or profiles with env substitutions.
    """
    
    __profiles = {
        'chipmunk-ard' : {
            'grid_fn':     partial(chipmunk.grid,
                                   url=env.get('CHIPMUNK_URL', None),
                                   resource=env.get('CHIPMUNK_GRID_RESOURCE', '/grid')),
            'dates_fn':    dates.symmetric,
            'chips_fn':    partial(chipmunk.chips,
                                   url=env.get('CHIPMUNK_URL', None),
                                   resource=env.get('CHIPMUNK_CHIPS_RESOURCE', '/chips')),
            'specs_fn':    partial(specs.mapped, ubids=ubids['chipmunk-ard']),
            'format_fn':   formats.pyccd,
            'registry_fn': partial(chipmunk.registry,
                                   url=env.get('CHIPMUNK_URL', None),
                                   resource=env.get('CHIPMUNK_REGISTRY_RESOURCE', '/registry')),
            'snap_fn':     partial(chipmunk.snap,
                                   url=env.get('CHIPMUNK_URL', None),
                                   resource=env.get('CHIPMUNK_SNAP_RESOURCE', '/grid/snap'))},
        'chipmunk-aux' : {
            'grid_fn':     partial(chipmunk.grid,
                                   url=env.get('CHIPMUNK_URL', None),
                                   resource=env.get('CHIPMUNK_GRID_RESOURCE', '/grid')),
            'dates_fn':    dates.symmetric,
            'chips_fn':    partial(chipmunk.chips,
                                   url=env.get('CHIPMUNK_URL', None),
                                   resource=env.get('CHIPMUNK_CHIPS_RESOURCE', '/chips')),
            'specs_fn':    partial(specs.mapped, ubids=ubids['chipmunk-aux']),
            'format_fn':   formats.pyccd,
            'registry_fn': partial(chipmunk.registry,
                                   url=env.get('CHIPMUNK_URL', None),
                                   resource=env.get('CHIPMUNK_REGISTRY_RESOURCE', '/registry')),
            'snap_fn':     partial(chipmunk.snap,
                                   url=env.get('CHIPMUNK_URL', None),
                                   resource=env.get('CHIPMUNK_SNAP_RESOURCE', '/grid/snap'))},
        }
    
    return __profiles.get(profile, None) if profile else __profiles


def get(profile='chipmunk-ard', env=None):
    """Return a configuration profile.

    Args:
        profile (str): Name of profile.
        env (dict): Environment variables to override os.environ
    Returns:
        dict: A Merlin configuration
    """
    
    p = profiles(env=merge(os.environ, env if env else {}),
                 profile=profile)

    return assoc(p, 'profile', profile)
