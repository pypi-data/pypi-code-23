# coding: utf-8
import os
import codecs
import json
import logging
from TileStache import parseConfig
from django_tilestache.caches import BaseCacheConfig
from django_tilestache.models import Layer
from django_tilestache.serializers import LayerSerializer
from django_tilestache.settings import settings
logger = logging.getLogger(__name__)


def get_config():

    """
    Gets a configuration
    """

    conf_man = ConfigurationManager()
    layers = Layer.objects.all()
    response = conf_man.build_config(cache=settings.TILESTACHE_CACHE,
                                     layers=layers)
    return response


def get_tilestache_config():

    """
    Gets the config for tilestache.
    this returns an object that can be used by
    tilestache and serve tiles.

    There is two methods, and while the method get_Config
    only gets a JSON representation, this one uses the former
    to construct a full TileStache object
    """
    return parseConfig(get_config())


class ConfigurationManager(object):

    LEFTOVER_FIELDS = ('id', )

    def read(self, path):
        pass

    def prepare_for_write(self, layer):
        """
        Prepare this layer for write.
        This means trimming up some extra
        fields that we have in Django, but
        we don't need them in tilestache
        """
        serializer = LayerSerializer(instance=layer)
        data = serializer.data
        for field in self.LEFTOVER_FIELDS:
            data.pop(field)
        name = data.pop('name')
        return {name: data}

    def build_config(self,
                     cache,
                     layers,
                     dirpath=None,
                     index=None):
        if not cache:
            cache_data = {
                'name': 'Test'
            }

        if isinstance(cache, dict):
            cache_data = cache

        if isinstance(cache, BaseCacheConfig):
            cache_data = cache.to_dict()

        layers_data = {}
        if layers:
            for layer in layers:
                layer_data = self.prepare_for_write(layer)
                layers_data.update(layer_data)

        return {
            'dirpath': dirpath,
            'cache': cache_data,
            'layers': layers_data
        }

    def serialize(self,
                  cache,
                  layers,
                  dirpath=None,
                  index=None,
                  indent=0):

        """
        Serializes a cache and layers config
        to json string
        """

        result = self.build_config(cache,
                                   layers,
                                   dirpath,
                                   index)
        return json.dumps(result, ensure_ascii=False, indent=indent)

    def write(self, path, cache, layers, dirpath=None, index=None, indent=0):
        """
        Writes a configuration to a location in disk
        indent must be an integer. it will be used
        as the number of spaces to pretty print the JSON
        """
        if not path:
            raise ValueError('path cannot be null')

        if not os.path.exists(os.path.dirname(path)):
            raise ValueError('directory %s does not exist.' % os.path.dirname(path))

        if index and not isinstance(index, tuple):
            raise ValueError('index must be two tuple')

        if not dirpath:
            dirpath = os.path.dirname(path)

        with codecs.open(path, 'w', 'utf-8') as cfg_file:
            cfg_file.write(self.serialize(
                cache,
                layers,
                dirpath=dirpath,
                index=index,
                indent=indent)
            )
