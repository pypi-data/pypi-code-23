"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from typing import Dict

from diskcache import Cache

from .types import Model
from .modelclient import ModelClient

## TODO: replace prints with logging.

class CacheHandler:

    def __init__(self, path):
        self.cache = Cache(path)

    def save_state(self, model: Model, key: str, data: object):
        print("Saving state to cache... key: {}".format(key))
        ## TODO: move _construct_serialized_model_path to Model?
        k = ModelClient._construct_serialized_model_path(model._id, 
                                                         model.name, 
                                                         key)
        ## NOTE: hacky, what's the best way to check if `data` is file-like?
        r = self.cache.add(k, data, read=hasattr(data, 'read'))
        if r:
            print("Saved {} to cache".format(k))
        else:
            print("{} already in cache. Nothing to do.".format(k))

    def load_state(self, model: Model, key: str) -> bytes:
        print("Loading state from cache... key: {}".format(key))
        k = ModelClient._construct_serialized_model_path(model._id, 
                                                         model.name, 
                                                         key)
        result = self.cache.get(k)
        if result:
            print("Loaded {} from cache".format(k))
        else:
            print("{} not in cache".format(k))
        return result

