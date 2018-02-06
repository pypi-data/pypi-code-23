# coding: utf-8
from TileStache import parseConfig
from .base import BaseConfiguration
from .utils import generate_coordinates
from .choices import DIRS_CHOICES


class BaseCacheConfig(BaseConfiguration):
    pass


class ExternalCacheConfig(BaseCacheConfig):

    """
    Configuration for external cache
    """

    klass = None
    arguments = None

    def is_valid(self):
        return self.klass is not None

    def _to_dict(self):
        dic = {'class': self.klass}
        if self.arguments:
            dic.update({'kwargs': self.arguments})
        return dic


class TestCacheConfig(BaseCacheConfig):

    """
    Configuration for test cache
    """

    verbose = True

    def _to_dict(self):
        return {
            'name': 'Test',
            'verbose': self.verbose
        }

    def is_valid(self):
        return isinstance(self.verbose, bool)


class DiskCacheConfig(BaseCacheConfig):

    """
    Configuration for disk cache
    """

    DIRS = [d[0] for d in DIRS_CHOICES]

    path = None
    umask = '0022'
    dirs = 'safe'
    gzip = ["txt", "text", "json", "xml"]

    def is_valid(self):
        return (self.path is not None and
                isinstance(self.path, basestring) and
                self.dirs in self.DIRS)

    def _to_dict(self):
        return {
            'name': 'Disk',
            'path': self.path,
            'umask': self.umask,
            'dirs': self.dirs,
            'gzip': self.gzip
        }


class MultiCacheConfig(BaseCacheConfig):

    """
    Configuration for multi cache
    """

    tiers = None

    def is_valid(self):
        if not self.tiers:
            return False
        return all([tier.is_valid() for tier in self.tiers])

    def _to_dict(self):
        tiers = [t.to_dict() for t in self.tiers]
        return {
            'name': 'Multi',
            'tiers': tiers
        }


class MemcacheCacheConfig(BaseCacheConfig):

    """
    Configuration for memcache cache
    """

    servers = None
    revision = 0
    key_prefix = ''

    def is_valid(self):
        # perhaps here we can do other validations
        return self.servers is not None

    def _to_dict(self):

        return {
            'name': 'Memcache',
            'servers': self.servers,
            'revision': self.revision,
            'key prefix': self.key_prefix
        }


class RedisCacheConfig(BaseCacheConfig):

    """
    Configuration for the redis cache
    """

    host = None
    port = 6379
    db = 0
    key_prefix = ''

    def is_valid(self):
        return self.host is not None and self.port is not None and self.db is not None

    def _to_dict(self):
        return {
            'name': 'Redis',
            'host': self.host,
            'port': self.port,
            'db': self.db,
            'key prefix': self.key_prefix
        }


class S3CacheConfig(BaseCacheConfig):

    """
    Configuration for S3 Cache
    """

    bucket = None
    access = None
    secret = None
    use_locks = True
    path = ''
    reduced_redundancy = False

    def is_valid(self):
        if self.access and not self.secret:
            return False

        if self.secret and not self.access:
            return False
        return self.bucket is not None

    def _to_dict(self):
        dic = {
            'name': 'S3',
            'bucket': self.bucket,
            'path': self.path,
            'use_locks': self.use_locks,
            'reduced_redundancy': self.reduced_redundancy
        }
        if self.access and self.secret:
            dic.update({
                'access': self.access,
                'secret': self.secret
            })
        return dic


class CacheManager(object):

    """
    Manages the Tilestache Cache.
    """

    ACTIONS = [
        '_seed_tile',
        '_purge_tile',
    ]

    def __init__(self, tilestache_cfg=None, **kwargs):
        if not tilestache_cfg:
            raise ValueError('tilestache_cfg is a required parameter')

        self.raw_config = tilestache_cfg
        # TODO: refatoar isto, pois pode ser um objeto também
        if isinstance(tilestache_cfg, basestring) or isinstance(tilestache_cfg, dict):
            self.config = parseConfig(tilestache_cfg)
        else:
            self.config = tilestache_cfg

    def _execute_action(self,
                        action,
                        layer,
                        geometry,
                        min_zoom=1,
                        max_zoom=21,
                        padding=0,
                        tile_format='PBF'):

        if not action:
            raise ValueError('action cannot be null')

        if action not in self.ACTIONS:
            raise ValueError('action must be one of %s' % ', '.join(self.ACTIONS.keys()))

        if not layer:
            raise ValueError('layer cannot be null')

        if isinstance(layer, basestring):
            tilestache_layer = self.config.layers.get(layer)
            if not layer:
                raise ValueError('layer %s is not available' % layer)
        else:
            tilestache_layer = layer

        if not geometry:
            # TODO: perhaps we can consider
            # that is the user does not provide an geometry
            # we will work on the entire cache
            raise ValueError('geometry cannot be null')

        action = getattr(self, action)
        tile_format = tile_format.upper()
        zooms = range(min_zoom, max_zoom + 1)
        coordinates = generate_coordinates(tilestache_layer,
                                           geometry,
                                           zooms,
                                           padding)

        for (offset, count, coord) in coordinates:
            action(tilestache_layer, coord, tile_format)

    def _seed_tile(self, layer, coord, tile_format):
        raise NotImplementedError('notimplemented')

    def _purge_tile(self, layer, coord, tile_format):
        '''removes a tile from the cache'''
        self.config.cache.remove(layer, coord, tile_format)

    def seed(self,
             layer,
             geometry,
             min_zoom=1,
             max_zoom=21,
             padding=0,
             tile_format='PBF'):
        self._execute_action(action='_seed_tile',
                             layer=layer,
                             geometry=geometry,
                             min_zoom=min_zoom,
                             max_zoom=max_zoom,
                             padding=0,
                             tile_format=tile_format)

    def purge(self,
              layer,
              geometry,
              min_zoom=1,
              max_zoom=21,
              padding=0,
              tile_format='PBF'):
        """
        purges the tilestache cache
        only inside the area of the
        geometry provided
        """
        self._execute_action(action='_purge_tile',
                             layer=layer,
                             geometry=geometry,
                             min_zoom=min_zoom,
                             max_zoom=max_zoom,
                             padding=0,
                             tile_format=tile_format)
